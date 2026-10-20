import { useState, useEffect } from 'react';
import type { SavedItem } from './types';
import { fetchItems } from './services/api';
import { Header } from './components/Header';
import { IngestCard } from './components/IngestCard';
import { QueryCard } from './components/QueryCard';
import { InboxList } from './components/InboxList';

export default function App() {
  const [items, setItems] = useState<SavedItem[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [globalError, setGlobalError] = useState<string | null>(null);

  const loadItems = async () => {
    try {
      setLoading(true);
      setGlobalError(null);
      const data = await fetchItems();
      setItems(data);
    } catch (err: any) {
      console.error('Failed to load items:', err);
      setGlobalError(err.message || 'Failed to connect to backend server');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadItems();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <Header />

      {/* Global Connection / System Error Alert */}
      {globalError && (
        <div className="max-w-6xl mx-auto px-4 pt-4">
          <div className="p-4 bg-amber-50 border border-amber-300 rounded-xl text-amber-900 text-xs flex items-center justify-between gap-4 shadow-xs">
            <div className="flex items-center gap-2">
              <span className="text-base">⚠️</span>
              <span className="font-medium">{globalError}</span>
            </div>
            <div className="flex items-center gap-2 shrink-0">
              <button
                type="button"
                onClick={loadItems}
                className="px-3 py-1 bg-amber-600 hover:bg-amber-700 text-white rounded-md font-semibold cursor-pointer text-xs"
              >
                Retry
              </button>
              <button
                type="button"
                onClick={() => setGlobalError(null)}
                className="text-amber-700 hover:text-amber-950 font-bold px-1.5 cursor-pointer text-sm"
              >
                ✕
              </button>
            </div>
          </div>
        </div>
      )}

      <main className="max-w-6xl mx-auto px-4 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Ingestion & Querying */}
        <div className="lg:col-span-7 space-y-8">
          <IngestCard onItemIngested={loadItems} />
          <QueryCard />
        </div>

        {/* Right Column: Knowledge Inbox */}
        <div className="lg:col-span-5">
          <InboxList items={items} loading={loading} />
        </div>
      </main>
    </div>
  );
}
