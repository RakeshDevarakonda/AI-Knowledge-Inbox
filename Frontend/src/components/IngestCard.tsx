import { useState } from 'react';
import { ingestContent } from '../services/api';

interface IngestCardProps {
  onItemIngested: () => void;
}

export const IngestCard = ({ onItemIngested }: IngestCardProps) => {
  const [activeTab, setActiveTab] = useState<'note' | 'url'>('note');
  const [noteContent, setNoteContent] = useState<string>('');
  const [noteTitle, setNoteTitle] = useState<string>('');
  const [urlInput, setUrlInput] = useState<string>('');
  const [urlTitle, setUrlTitle] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setMessage(null);
    setLoading(true);

    try {
      if (activeTab === 'note') {
        if (!noteContent.trim()) {
          setMessage({ type: 'error', text: 'Please enter note content.' });
          setLoading(false);
          return;
        }
        await ingestContent({
          source_type: 'note',
          content: noteContent.trim(),
          title: noteTitle.trim() || undefined,
        });
        setNoteContent('');
        setNoteTitle('');
      } else {
        if (!urlInput.trim()) {
          setMessage({ type: 'error', text: 'Please enter a valid webpage URL.' });
          setLoading(false);
          return;
        }
        await ingestContent({
          source_type: 'url',
          url: urlInput.trim(),
          title: urlTitle.trim() || undefined,
        });
        setUrlInput('');
        setUrlTitle('');
      }

      setMessage({
        type: 'success',
        text: `${activeTab === 'note' ? 'Note' : 'URL content'} saved and indexed!`,
      });
      onItemIngested();
    } catch (err: any) {
      setMessage({ type: 'error', text: err.message || 'Failed to ingest content' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs overflow-hidden">
      <div className="p-4 border-b border-slate-100 flex items-center justify-between">
        <h2 className="font-semibold text-slate-800 text-sm tracking-wide uppercase">1. Ingest Content</h2>
        
        {/* Tab Toggle */}
        <div className="inline-flex p-1 bg-slate-100 rounded-lg text-xs font-medium">
          <button
            type="button"
            onClick={() => { setActiveTab('note'); setMessage(null); }}
            className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
              activeTab === 'note'
                ? 'bg-white text-indigo-700 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            📝 Text Note
          </button>
          <button
            type="button"
            onClick={() => { setActiveTab('url'); setMessage(null); }}
            className={`px-3 py-1 rounded-md transition-all cursor-pointer ${
              activeTab === 'url'
                ? 'bg-white text-indigo-700 shadow-xs font-semibold'
                : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            🔗 Web URL
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-5 space-y-4">
        {activeTab === 'note' ? (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Title (Optional)</label>
              <input
                type="text"
                placeholder="e.g., Team Meeting Notes"
                value={noteTitle}
                onChange={(e) => setNoteTitle(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">
                Note Content <span className="text-red-500">*</span>
              </label>
              <textarea
                rows={4}
                placeholder="Paste your plain text or ideas here..."
                value={noteContent}
                onChange={(e) => setNoteContent(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </>
        ) : (
          <>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">
                Webpage URL <span className="text-red-500">*</span>
              </label>
              <input
                type="url"
                placeholder="https://example.com/article"
                value={urlInput}
                onChange={(e) => setUrlInput(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
              <p className="text-xs text-slate-400 mt-1">Server fetches the page and strips HTML tags automatically.</p>
            </div>
            <div>
              <label className="block text-xs font-medium text-slate-600 mb-1">Custom Title (Optional)</label>
              <input
                type="text"
                placeholder="Leave empty to use website's page title"
                value={urlTitle}
                onChange={(e) => setUrlTitle(e.target.value)}
                className="w-full px-3 py-2 text-sm border border-slate-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              />
            </div>
          </>
        )}

        {/* Feedback Message */}
        {message && (
          <div
            className={`p-3 rounded-lg text-xs font-medium flex items-start justify-between gap-2 animate-in fade-in ${
              message.type === 'success'
                ? 'bg-emerald-50 text-emerald-800 border border-emerald-200'
                : 'bg-rose-50 text-rose-800 border border-rose-200'
            }`}
          >
            <div className="flex items-start gap-2">
              <span className="text-sm">{message.type === 'success' ? '✅' : '⚠️'}</span>
              <span className="leading-relaxed">{message.text}</span>
            </div>
            <button
              type="button"
              onClick={() => setMessage(null)}
              className="font-bold opacity-60 hover:opacity-100 text-sm px-1 cursor-pointer"
              title="Dismiss"
            >
              ✕
            </button>
          </div>
        )}

        <button
          type="submit"
          disabled={loading}
          className="w-full py-2.5 px-4 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-semibold shadow-xs disabled:opacity-50 transition-colors cursor-pointer"
        >
          {loading ? 'Processing & Embedding Chunks...' : activeTab === 'note' ? 'Save Note' : 'Scrape & Ingest URL'}
        </button>
      </form>
    </div>
  );
};
