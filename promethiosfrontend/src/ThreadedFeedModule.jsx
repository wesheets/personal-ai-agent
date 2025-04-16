import ThreadedComment from "./ThreadedComment";

export default function ThreadedFeedModule({ thread = [] }) {
  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-6">
      {thread.map((msg, idx) => (
        <ThreadedComment
          key={idx}
          role={msg.role}
          content={msg.content}
          replies={msg.replies}
        />
      ))}
    </div>
  );
}
