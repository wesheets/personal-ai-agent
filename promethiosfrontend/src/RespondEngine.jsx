export default async function RespondEngine({ message }) {
  try {
    const response = await fetch("/api/respond", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });

    if (!response.ok) throw new Error("Agent response failed");

    const data = await response.json();
    return data.output || "✅ Agent responded, but no content returned.";
  } catch (err) {
    console.error("RespondEngine error:", err);
    return "❌ Agent is offline or unavailable.";
  }
}
