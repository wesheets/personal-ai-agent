import { useEffect, useRef, useState } from "react";
import AgentOutputBubble from "./AgentOutputBubble";
import AgentInputBar from "./AgentInputBar";
import RespondEngine from "./RespondEngine";

export default function AgentChatPanel() {
  const [messages, setMessages] = useState([
    { role: "agent", content: "🧠 Promethios OS booted. Welcome, Operator." }
  ]);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleSend(content) {
    if (!content.trim()) return;

    // Add operator message
    setMessages((prev) => [...prev, { role: "operator", content }]);

    // Call RespondEngine to simulate/trigger agent
    const agentReply = await RespondEngine({ message: content });

    // Add agent reply
    setMessages((prev) => [
      ...prev,
      { role: "agent", content: agentReply }
    ]);
  }

  return (
    <div className="flex flex-col h-full overflow-hidden">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <AgentOutputBubble key={idx} role={msg.role} content={msg.content} />
        ))}
        <div ref={bottomRef} />
      </div>
      <AgentInputBar onSend={handleSend} />
    </div>
  );
}
