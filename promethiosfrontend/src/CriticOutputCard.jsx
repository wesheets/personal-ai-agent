export default function CriticOutputCard({ score, feedback }) {
  return (
    <div className="bg-red-900 p-4 rounded-xl shadow-md mt-4 border border-red-400">
      <h3 className="text-lg font-bold text-red-200 mb-2">🎯 CRITIC Evaluation</h3>
      <p>
        <strong>Score:</strong> {score || 'N/A'}/10
      </p>
      <p className="italic text-red-100 mt-2">{feedback || 'No feedback available.'}</p>
    </div>
  );
}
