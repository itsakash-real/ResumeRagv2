

import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAuthStore = create(
  persist(
    (set) => ({
      user: null,
      token: null,

      get isAuthenticated() {
        // Computed from token — cannot drift out of sync
        return !!this.token;
      },

      setAuth: (user, token) => set({ user, token }),

      logout: () => set({ user: null, token: null }),
    }),
    {
      name: 'auth-storage', // localStorage key — matches api.js interceptor
      partialize: (state) => ({ user: state.user, token: state.token }),
    }
  )
);

export default useAuthStore;