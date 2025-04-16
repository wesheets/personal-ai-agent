export default function ThreadedComment({ role, content, replies = [] }) {
  const isOperator = role === "operator";

  return (
    <div className={`flex ${isOperator ? "justify-end" : "justify-start"}`}>
      <div className={`max-w-[70%] px-4 py-3 rounded-xl shadow-md whitespace-pre-wrap
        ${isOperator
          ? "bg-teal-500 text-white rounded-br-none"
          : "bg-gray-800 text-gray-100 rounded-bl-none"
        }`}>
        <p className="text-sm">{content}</p>

        {replies.length > 0 && (
          <div className="mt-3 border-l border-gray-600 pl-3 space-y-3">
            {replies.map((reply, i) => (
              <ThreadedComment
                key={i}
                role={reply.role}
                content={reply.content}
                replies={reply.replies}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
