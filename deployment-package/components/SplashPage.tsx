import React from 'react';
import Typewriter from 'typewriter-effect';
import LoginForm from './LoginForm';

interface SplashPageProps {
  onLogin: (username: string, password: string) => void;
  error: string | null;
}

const SplashPage: React.FC<SplashPageProps> = ({ onLogin, error }) => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-black text-white p-4">
      <div className="max-w-md w-full flex flex-col items-center">
        {/* Logo with fade-in animation */}
        <div className="animate-fade-in mb-8">
          <img 
            src="/promethioslogo.png" 
            alt="Promethios logo" 
            className="max-w-[220px] w-full"
          />
        </div>
        
        {/* Typed animation slogan */}
        <div className="text-xl text-center mb-8 h-16">
          <Typewriter
            options={{
              strings: ['The fire has been lit. Operator input required.'],
              autoStart: true,
              loop: false,
              delay: 50,
            }}
          />
        </div>
        
        {/* Login Form */}
        <LoginForm onLogin={onLogin} error={error} />
      </div>
    </div>
  );
};

export default SplashPage;
