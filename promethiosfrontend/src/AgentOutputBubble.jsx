export default function AgentOutputBubble({ role, content }) {
  const isOperator = role === "operator";

  return (
    <div className={`flex ${isOperator ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[70%] px-4 py-2 rounded-xl text-sm whitespace-pre-wrap shadow-md ${
          isOperator
            ? "bg-teal-500 text-white rounded-br-none"
            : "bg-gray-800 text-gray-100 rounded-bl-none"
        }`}
      >
        {content}
      </div>
    </div>
  );
}
