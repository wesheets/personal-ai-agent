import { useState, useEffect } from 'react';

export default function GlitchCountdown() {
  const [countdown, setCountdown] = useState('130 : 13 : 01 : 23');

  useEffect(() => {
    const interval = setInterval(() => {
      if (Math.random() > 0.92) {
        setCountdown('LOOP FAILED – REBUILDING…');
        setTimeout(() => setCountdown('130 : 13 : 01 : 23'), 3000);
      }
    }, 5000);
    return () => clearInterval(interval);
  }, []);

  return <div className="text-xl mt-4 font-mono z-10">{countdown}</div>;
}
