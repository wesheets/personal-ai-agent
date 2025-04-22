import React from 'react';
import VideoBackground from './VideoBackground';
import GlitchCountdown from './GlitchCountdown';
import SloganReveal from './SloganReveal';
import WaitlistForm from './WaitlistForm';
import LoginGate from './LoginGate';

const SplashScreen = () => {
  return (
    <div className="relative flex flex-col justify-center items-center h-screen text-white bg-black overflow-hidden">
      <VideoBackground />
      <img src="/assets/promethioslogo.png" alt="Promethios Logo" className="w-64 mb-8 z-10" />
      <SloganReveal />
      <GlitchCountdown />
      <WaitlistForm />
      <LoginGate />
    </div>
  );
};

export default SplashScreen;
