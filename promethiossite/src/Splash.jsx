import React from "react";

export default function SplashPage() {
  return (
    <div className="flex h-screen w-full bg-black text-white">
      {/* Left Panel */}
      <div className="w-[460px] flex flex-col justify-center items-center px-10">
        <img src="/logo.png" alt="Promethios Logo" className="max-w-[160px] mb-6" />
        <h1 className="text-2xl font-bold mb-2">Promethios Operator Dashboard</h1>
        <p className="text-sm text-gray-400 mb-6">
          The fire has been lit. Operator input required.
        </p>
        <form className="w-full space-y-4">
          <input
            type="text"
            placeholder="Username"
            className="w-full bg-gray-900 border border-gray-700 p-3 rounded-md"
          />
          <input
            type="password"
            placeholder="Password"
            className="w-full bg-gray-900 border border-gray-700 p-3 rounded-md"
          />
          <button
            type="submit"
            className="w-full bg-indigo-500 hover:bg-indigo-600 text-white p-3 rounded-md font-semibold"
          >
            Enter Control Room
          </button>
          {/* Access Denied Message Placeholder */}
          {/* <p className="text-sm text-red-500 text-center">Access denied. 🔒 Invalid credentials.</p> */}
        </form>
      </div>

      {/* Right Panel */}
      <div className="flex-1 bg-gradient-to-br from-black to-gray-900 flex items-center justify-center">
        {/* Optional: Background effects like ember particles, quote, or animation */}
        <img
          src="/c52729f1-be7b-4311-bad8-e0081c72130d.png"
          alt="Promethios Graphic"
          className="max-w-[60%] opacity-80"
        />
      </div>
    </div>
  );
}
