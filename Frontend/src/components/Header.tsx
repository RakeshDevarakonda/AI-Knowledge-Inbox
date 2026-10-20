export const Header = () => {
  return (
    <header className="border-b border-slate-200 bg-white sticky top-0 z-30 shadow-xs">
      <div className="max-w-6xl mx-auto px-4 py-3 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="h-9 w-9 rounded-lg bg-indigo-600 text-white flex items-center justify-center font-bold text-lg shadow-sm">
            AI
          </div>
          <div>
            <h1 className="text-lg font-bold text-slate-900 leading-tight">AI Knowledge Inbox</h1>
            <p className="text-xs text-slate-500">Minimal RAG Pipeline • Notes & URLs</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-emerald-50 text-emerald-700 border border-emerald-200">
            <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Backend Active
          </span>
        </div>
      </div>
    </header>
  );
};
