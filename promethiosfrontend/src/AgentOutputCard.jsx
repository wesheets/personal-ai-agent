export default function AgentOutputCard({ title, content }) {
  return (
    <div className="bg-gray-800 p-4 rounded-xl shadow-md mt-4 border border-gray-700">
      <h3 className="text-lg font-semibold mb-2 text-teal-300">{title}</h3>
      <p className="whitespace-pre-line text-gray-100">{content || 'No data available.'}</p>
    </div>
  );
}
