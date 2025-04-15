import { useEffect, useRef, useState } from "react";
import AgentOutputBubble from "./AgentOutputBubble";
import AgentInputBar from "./AgentInputBar";

export default function AgentChatPanel() {
  const [messages, setMessages] = useState([
    { role: "agent", content: "System initialized. Welcome, Operator." },
    { role: "operator", content: "Show me the latest agent summary." }
  ]);

  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  function handleSend(content) {
    if (!content.trim()) return;
    setMessages((prev) => [...prev, { role: "operator", content }]);

    // Simulate agent response
    setTimeout(() => {
      setMessages((prev) => [
        ...prev,
        {
          role: "agent",
          content: `Acknowledged. Processing request: "${content}".`
        }
      ]);
    }, 500);
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
