import { marked } from "marked";

export default function AgentMarkdownRenderer({ content }) {
  if (!content) return null;

  const html = marked.parse(content, {
    breaks: true,
  });

  return (
    <div
      className="prose prose-invert max-w-none text-sm leading-relaxed"
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
}
