import { useState } from 'react';

export default function WaitlistForm() {
  const [email, setEmail] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const payload = {
      email,
      timestamp: new Date().toISOString(),
      project_id: "waitlist_promethios",
      schema_compliant: true
    };
    await fetch("https://formspree.io/f/YOUR_ID", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    setSubmitted(true);
  };

  return (
    <form onSubmit={handleSubmit} className="flex flex-col items-center z-10">
      {submitted ? (
        <p className="text-green-400">You're on the list.</p>
      ) : (
        <>
          <input
            type="email"
            placeholder="you@domain.com"
            className="text-black px-4 py-2 rounded-md"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
          <button className="bg-white text-black px-4 py-2 mt-2 rounded-md">Join Waitlist</button>
        </>
      )}
    </form>
  );
}
