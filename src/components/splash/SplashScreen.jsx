import React from 'react';
import VideoBackground from './VideoBackground';
import GlitchCountdown from './GlitchCountdown';
import SloganReveal from './SloganReveal';
import WaitlistForm from './WaitlistForm';
import LoginGate from './LoginGate';

const SplashScreen = () => {
  return (
    <div className="relative h-screen w-full overflow-hidden bg-black text-white">
      <VideoBackground />

      <div className="relative z-10 flex flex-col justify-center items-center h-full">
        <img
          src="/assets/promethioslogo.png"
          alt="Promethios Logo"
          className="w-64 mb-8"
        />
        <SloganReveal />
        <GlitchCountdown />
        <WaitlistForm />
        <LoginGate />
      </div>
    </div>
  );
};

export default SplashScreen;
