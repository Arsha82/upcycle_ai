import React, { useState, useEffect, useRef } from 'react';
import { useThemeStore } from '../../themeStore';
import { useBgModeStore } from '../../bgModeStore';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

export const BackgroundEngine: React.FC = () => {
  const theme = useThemeStore((state) => state.theme);
  const bgMode = useBgModeStore((state: any) => state.bgMode);
  const [vantaEffect, setVantaEffect] = useState<any>(null);
  const vantaRef = useRef<HTMLDivElement>(null);

  // Mount / destroy Vanta only when in 'vanta' mode
  useEffect(() => {
    if (bgMode !== 'vanta') {
      if (vantaEffect) { vantaEffect.destroy(); setVantaEffect(null); }
      return;
    }
    if (!vantaEffect && vantaRef.current && (window as any).VANTA) {
      const effect = (window as any).VANTA.BIRDS({
        el: vantaRef.current,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200,
        minWidth: 200,
        scale: 1,
        scaleMobile: 1,
        backgroundColor: theme === 'dark' ? 0x0a100d : 0xffffff,
        color1: theme === 'dark' ? 0x1b4332 : 0xca008a,
        color2: theme === 'dark' ? 0xa3c2b0 : 0x00ff9f,
        birdSize: theme === 'dark' ? 1.5 : 1.9,
        wingSpan: 32,
        separation: 48,
        alignment: 56,
        cohesion: 35,
        quantity: 4,
      });
      setVantaEffect(effect);
    }
    return () => {
      if (vantaEffect) { vantaEffect.destroy(); setVantaEffect(null); }
    };
  }, [bgMode]);

  // Sync colors when theme changes while in Vanta mode
  useEffect(() => {
    if (vantaEffect && bgMode === 'vanta') {
      vantaEffect.setOptions({
        backgroundColor: theme === 'dark' ? 0x0a100d : 0xffffff,
        color1: theme === 'dark' ? 0x1b4332 : 0xca008a,
        color2: theme === 'dark' ? 0xa3c2b0 : 0x00ff9f,
        birdSize: theme === 'dark' ? 1.5 : 1.9,
      });
    }
  }, [theme, vantaEffect, bgMode]);

  if (bgMode === 'lottie') {
    return (
      <div className="fixed inset-0 w-full h-full z-[-50] overflow-hidden">
        {/* Lottie animation fills the whole background */}
        <div className="absolute inset-0 w-full h-full flex items-center justify-center pointer-events-none">
          <DotLottieReact
            src="/nature.lottie"
            loop
            autoplay
            className="w-full h-full [&>canvas]:!object-cover [&>canvas]:!w-full [&>canvas]:!h-full"
          />
        </div>
        {/* Overlay adjusts based on theme for readability */}
        <div className={`absolute inset-0 transition-colors duration-700 ${
          theme === 'dark'
            ? 'bg-[#060d08]/70'
            : 'bg-white/30'
        }`} />
      </div>
    );
  }

  // Vanta mode
  return (
    <div className="fixed inset-0 w-full h-full z-[-50]">
      <div ref={vantaRef} className="absolute inset-0 w-full h-full" />
    </div>
  );
};
