import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const SPLASH_KEY = 'papervault-splash-seen';

export function SplashIntro({ onComplete }: { onComplete: () => void }) {
  const [phase, setPhase] = useState<'materialize' | 'snap' | 'exit'>('materialize');

  useEffect(() => {
    const snapTimer = window.setTimeout(() => setPhase('snap'), 850);
    const exitTimer = window.setTimeout(() => setPhase('exit'), 1650);
    const doneTimer = window.setTimeout(() => {
      sessionStorage.setItem(SPLASH_KEY, '1');
      onComplete();
    }, 2100);

    return () => {
      clearTimeout(snapTimer);
      clearTimeout(exitTimer);
      clearTimeout(doneTimer);
    };
  }, [onComplete]);

  return (
    <motion.div
      className="fixed inset-0 z-[100] flex items-center justify-center bg-base-100"
      initial={{ opacity: 1 }}
      animate={{ opacity: phase === 'exit' ? 0 : 1 }}
      transition={{ duration: 0.45, ease: 'easeInOut' }}
    >
      <motion.div
        initial={{ opacity: 0, filter: 'blur(16px)', scale: 0.88, y: 8 }}
        animate={
          phase === 'materialize'
            ? { opacity: 0.85, filter: 'blur(4px)', scale: 1.04, y: 0 }
            : { opacity: 1, filter: 'blur(0px)', scale: 1, y: 0 }
        }
        transition={
          phase === 'materialize'
            ? { duration: 0.85, ease: [0.22, 1, 0.36, 1] }
            : { type: 'spring', stiffness: 520, damping: 32, mass: 0.85 }
        }
        className="text-center select-none"
      >
        <h1 className="text-6xl sm:text-7xl md:text-8xl font-black tracking-tighter leading-none text-base-content">
          Paper<span className="text-primary">Vault</span>
        </h1>
        <AnimatePresence>
          {phase !== 'materialize' && (
            <motion.p
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              className="mt-4 text-xs font-mono uppercase tracking-[0.35em] text-base-content/35"
            >
              Research intelligence
            </motion.p>
          )}
        </AnimatePresence>
      </motion.div>
    </motion.div>
  );
}
