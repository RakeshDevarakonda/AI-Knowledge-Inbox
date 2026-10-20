import { useState } from 'react';
import type { SavedItem } from '../types';

interface InboxListProps {
  items: SavedItem[];
  loading: boolean;
}

export const InboxList = ({ items, loading }: InboxListProps) => {
  const [filterType, setFilterType] = useState<'all' | 'note' | 'url'>('all');

  const filteredItems = items.filter((item) => {
    if (filterType === 'all') return true;
    return item.source_type === filterType;
  });

  return (
    <div className="bg-white rounded-xl border border-slate-200 shadow-xs sticky top-20">
      <div className="p-4 border-b border-slate-100 flex items-center justify-between">
        <div>
          <h2 className="font-semibold text-slate-800 text-sm tracking-wide uppercase">3. Saved Inbox</h2>
          <span className="text-xs text-slate-500">{items.length} item{items.length === 1 ? '' : 's'} stored</span>
        </div>

        {/* Filter Pills */}
        <div className="flex items-center gap-1 bg-slate-100 p-0.5 rounded-lg text-xs">
          {(['all', 'note', 'url'] as const).map((type) => (
            <button
              key={type}
              onClick={() => setFilterType(type)}
              className={`px-2 py-0.5 rounded capitalize cursor-pointer ${
                filterType === type ? 'bg-white font-semibold shadow-2xs text-slate-900' : 'text-slate-600'
              }`}
            >
              {type}
            </button>
          ))}
        </div>
      </div>

      {/* Items List */}
      <div className="p-4 max-h-[calc(100vh-200px)] overflow-y-auto space-y-3">
        {loading ? (
          <div className="py-12 text-center text-xs text-slate-400">Loading saved items...</div>
        ) : filteredItems.length === 0 ? (
          <div className="py-12 text-center text-slate-400 text-xs">
            No {filterType !== 'all' ? filterType : ''} items saved yet. Use the form to ingest your first note or link!
          </div>
        ) : (
          filteredItems.map((item) => (
            <div
              key={item.id}
              className="p-3 rounded-lg border border-slate-200 hover:border-slate-300 transition-colors bg-white shadow-2xs space-y-1.5"
            >
              <div className="flex items-center justify-between gap-2">
                <span
                  className={`text-[10px] uppercase font-bold px-1.5 py-0.5 rounded ${
                    item.source_type === 'note'
                      ? 'bg-purple-50 text-purple-700 border border-purple-200'
                      : 'bg-blue-50 text-blue-700 border border-blue-200'
                  }`}
                >
                  {item.source_type}
                </span>
                <span className="text-[10px] text-slate-400">
                  {new Date(item.created_at).toLocaleDateString([], {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>

              <h4 className="font-semibold text-xs text-slate-900 leading-snug line-clamp-1">
                {item.title}
              </h4>

              <p className="text-slate-600 text-xs line-clamp-2">
                {item.content}
              </p>

              {item.source_url && (
                <a
                  href={item.source_url}
                  target="_blank"
                  rel="noreferrer"
                  className="text-[11px] text-indigo-600 hover:underline block truncate"
                >
                  🔗 {item.source_url}
                </a>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};
