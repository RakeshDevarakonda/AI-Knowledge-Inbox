import { useState } from 'react';
import { askQuestion } from '../services/api';
import type { QueryResponse } from '../types';

export const QueryCard = () => {
  const [question, setQuestion] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleQuery = async (e: React.FormEvent) => {
    e.preventDefault();
    const queryText = question.trim();
    if (!queryText) return;

    // Clear input box immediately after clicking Ask AI
    setQuestion('');
    setLoading(true);
    setError(null);

    try {
      const response = await askQuestion(queryText, 3);
      setResult(response);
    } catch (err: any) {
      setError(err.message || 'Error querying knowledge base');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="p-4 border-b border-slate-100">
        <h2 className="font-semibold text-slate-800 text-sm tracking-wide uppercase">2. Ask Question (RAG Search)</h2>
        <p className="text-xs text-slate-500">Retrieves relevant chunks and synthesizes an answer with citations.</p>
      </div>

      <form onSubmit={handleQuery} className="p-5 space-y-3">
        <div className="flex gap-2">
          <input
            type="text"
            placeholder="e.g., How many books can a member borrow, and for how many days?"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            className="flex-1 px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
          />
          <button
            type="submit"
            disabled={loading || !question.trim()}
            className="px-5 py-2 bg-slate-900 hover:bg-slate-800 text-white text-sm font-medium rounded-lg disabled:opacity-50 transition-colors cursor-pointer"
          >
            {loading ? 'Synthesizing...' : 'Ask AI'}
          </button>
        </div>

        {/* Global Error Banner */}
        {error && (
          <div className="p-3 bg-rose-50 text-rose-800 border border-rose-200 rounded-lg text-xs flex items-start justify-between gap-2 animate-in fade-in">
            <div className="flex items-start gap-2">
              <span className="text-rose-600 text-sm font-bold">⚠️</span>
              <span className="font-medium leading-relaxed">{error}</span>
            </div>
            <button
              type="button"
              onClick={() => setError(null)}
              className="text-rose-500 hover:text-rose-800 font-bold px-1 text-sm cursor-pointer"
              title="Dismiss error"
            >
              ✕
            </button>
          </div>
        )}
      </form>

      {/* Answer Box */}
      {result && (
        <div className="p-5 border-t border-slate-100 bg-slate-50/50 space-y-4">
          <div>
            <div className="flex items-center gap-2 mb-1.5">
              <span className="text-xs font-bold uppercase tracking-wider text-indigo-700 bg-indigo-50 px-2 py-0.5 rounded">
                Answer
              </span>
              <span className="text-xs text-slate-400 truncate">"{result.question}"</span>
            </div>
            <div className="text-sm text-slate-800 leading-relaxed bg-white p-4 rounded-lg border border-slate-200 whitespace-pre-wrap shadow-2xs">
              {result.answer}
            </div>
          </div>

          {/* Sources Section */}
          {result.sources.length > 0 && (
            <div>
              <h3 className="text-xs font-semibold text-slate-600 uppercase tracking-wider mb-2">
                Cited Sources ({result.sources.length})
              </h3>
              <div className="space-y-2">
                {result.sources.map((src) => (
                  <div
                    key={src.source_id}
                    className="bg-white p-3 rounded-lg border border-slate-200 text-xs space-y-1 shadow-2xs"
                  >
                    <div className="flex items-center justify-between">
                      <span className="font-semibold text-indigo-700">
                        📄 {src.title}
                      </span>
                      <span className="text-[11px] font-mono text-slate-500 bg-slate-100 px-1.5 py-0.5 rounded">
                        Score: {(src.similarity_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <p className="text-slate-600 italic">"{src.snippet}"</p>
                    {src.source_url && (
                      <a
                        href={src.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-indigo-600 hover:underline block truncate text-[11px]"
                      >
                        🔗 {src.source_url}
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
