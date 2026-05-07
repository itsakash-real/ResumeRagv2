

import io
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from httpx import AsyncClient


# ── Minimal valid PDF bytes (hand-crafted, not a real document) ───────────────
# This is the smallest structurally valid PDF that passes magic byte check.
MINIMAL_PDF_BYTES = (
    b"%PDF-1.4\n"
    b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
    b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
    b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
    b"/Contents 4 0 R /Resources << /Font << /F1 << /Type /Font "
    b"/Subtype /Type1 /BaseFont /Helvetica >> >> >> >>\nendobj\n"
    b"4 0 obj\n<< /Length 44 >>\nstream\n"
    b"BT /F1 12 Tf 100 700 Td (Hello Resume) Tj ET\n"
    b"endstream\nendobj\n"
    b"xref\n0 5\n"
    b"0000000000 65535 f \n"
    b"0000000009 00000 n \n"
    b"0000000068 00000 n \n"
    b"0000000125 00000 n \n"
    b"0000000266 00000 n \n"
    b"trailer\n<< /Size 5 /Root 1 0 R >>\n"
    b"startxref\n359\n%%EOF"
)


def _auth_headers(access_token: str) -> dict:
    """Returns Authorization header dict for a given JWT access token."""
    return {"Authorization": f"Bearer {access_token}"}


# ── Upload tests ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_upload_no_file(client: AsyncClient, test_user: dict) -> None:
    """POST /resume/upload with no file attached → 422."""
    response = await client.post(
        "/resume/upload",
        headers=_auth_headers(test_user["access_token"]),
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_upload_invalid_magic_bytes(client: AsyncClient, test_user: dict) -> None:
    """
    POST /resume/upload with a text file renamed to .pdf.
    Magic bytes are not %PDF → 400.
    """
    fake_pdf = io.BytesIO(b"This is plain text, not a PDF at all.")
    response = await client.post(
        "/resume/upload",
        headers=_auth_headers(test_user["access_token"]),
        files={"file": ("resume.pdf", fake_pdf, "application/pdf")},
    )
    assert response.status_code == 400
    assert "invalid file type" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_upload_file_too_large(client: AsyncClient, test_user: dict) -> None:
    """
    POST /resume/upload with a file exceeding 5 MB → 413.
    We prepend valid PDF magic bytes followed by padding to exceed the limit.
    """
    oversized = b"%PDF" + (b"x" * (5 * 1024 * 1024 + 1))
    response = await client.post(
        "/resume/upload",
        headers=_auth_headers(test_user["access_token"]),
        files={"file": ("big.pdf", io.BytesIO(oversized), "application/pdf")},
    )
    assert response.status_code == 413


@pytest.mark.asyncio
async def test_upload_valid_pdf(client: AsyncClient, test_user: dict) -> None:
    """
    POST /resume/upload with a structurally valid minimal PDF.
    parse_pdf is mocked so we don't need a real pdfplumber-readable file.
    """
    with patch(
        "routers.resume.parse_pdf",
        return_value="Python developer with 5 years of experience in FastAPI and PostgreSQL. " * 5,
    ):
        response = await client.post(
            "/resume/upload",
            headers=_auth_headers(test_user["access_token"]),
            files={"file": ("resume.pdf", io.BytesIO(MINIMAL_PDF_BYTES), "application/pdf")},
        )

    assert response.status_code == 201
    body = response.json()
    assert "resume_id" in body
    assert isinstance(body["resume_id"], str)
    assert len(body["resume_id"]) == 36  # UUID v4 format
    assert body["char_count"] > 0


@pytest.mark.asyncio
async def test_upload_requires_auth(client: AsyncClient) -> None:
    """POST /resume/upload without token → 401."""
    response = await client.post(
        "/resume/upload",
        files={"file": ("resume.pdf", io.BytesIO(MINIMAL_PDF_BYTES), "application/pdf")},
    )
    assert response.status_code == 401


# ── Rate limiting test ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_match_rate_limit(client: AsyncClient, test_user: dict) -> None:
    from main import limiter
    limiter.reset()
    """
    POST /resume/match is limited to 10 requests/hour per IP.
    The 11th request within the window must return 429.

    The entire AI pipeline is mocked so this test runs in milliseconds
    and does not require real API keys or a GPU.
    """
    # We need a resume_id in the DB first — upload one
    with patch(
        "routers.resume.parse_pdf",
        return_value="Software engineer with experience in Python. " * 10,
    ):
        upload_resp = await client.post(
            "/resume/upload",
            headers=_auth_headers(test_user["access_token"]),
            files={"file": ("resume.pdf", io.BytesIO(MINIMAL_PDF_BYTES), "application/pdf")},
        )
    assert upload_resp.status_code == 201
    resume_id = upload_resp.json()["resume_id"]

    mock_profile = {
        "skills": ["Python", "FastAPI", "PostgreSQL"],
        "experience_years": 5,
        "job_titles": ["Software Engineer"],
        "summary": "Experienced Python engineer specializing in backend systems.",
    }
    mock_jobs = [
        {
            "title": "Backend Engineer",
            "company": "Acme Corp",
            "location": "Remote",
            "url": "https://example.com/job/1",
            "description": "Python FastAPI backend role.",
            "salary_min": 90000.0,
            "salary_max": 130000.0,
        }
    ]

    import numpy as np

    with (
        patch("routers.resume.extract_profile", return_value=mock_profile),
        patch("routers.resume.fetch_jobs", new_callable=AsyncMock, return_value=mock_jobs),
        patch("routers.resume.embed_text", return_value=np.random.rand(384).astype(np.float32)),
        patch("routers.resume.embed_batch", return_value=np.random.rand(1, 384).astype(np.float32)),
        patch("routers.resume.build_index", return_value=MagicMock()),
        patch("routers.resume.query_index", return_value=[(0, 0.92)]),

        patch("routers.resume.save_match_results"),
    ):
        responses = []
        for _ in range(11):
            resp = await client.post(
                "/resume/match",
                headers=_auth_headers(test_user["access_token"]),
                json={"resume_id": resume_id},
            )
            responses.append(resp.status_code)

    print("RESPONSES", responses)
    # First 10 must succeed (200), 11th must be rate limited (429)
    assert all(code == 200 for code in responses[:10]), (
        f"Expected all 200s in first 10, got: {responses[:10]}"
    )
    assert responses[10] == 429, (
        f"Expected 429 on 11th request, got: {responses[10]}"
    )