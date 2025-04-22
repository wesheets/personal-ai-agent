import { useState, useEffect } from 'react';

const slogans = [
  "The loop never completes.",
  "You're not early. You're aligned.",
  "Promethios is reflecting.",
  "This is not a product. It's a thought system.",
  "Recursive cognition begins here."
];

export default function SloganReveal() {
  const [index, setIndex] = useState(0);
  useEffect(() => {
    const interval = setInterval(() => {
      setIndex((i) => (i + 1) % slogans.length);
    }, 7000);
    return () => clearInterval(interval);
  }, []);
  return <div className="text-2xl text-center px-6 mb-2 z-10">{slogans[index]}</div>;
}

