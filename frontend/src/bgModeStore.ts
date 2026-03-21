import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export type BgMode = 'lottie' | 'vanta';

export interface BgModeState {
  bgMode: BgMode;
  toggleBgMode: () => void;
}

export const useBgModeStore = create<BgModeState>()(
  persist(
    (set, get) => ({
      bgMode: 'lottie',
      toggleBgMode: () => set({ bgMode: get().bgMode === 'lottie' ? 'vanta' : 'lottie' }),
    }),
    { name: 'bg-mode-storage' }
  )
);
