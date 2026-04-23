import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Search, FileText, ExternalLink, User, Calendar, X } from 'lucide-react';

import { LiquidButton } from '@/components/animate-ui/components/buttons/liquid';

interface Source {
  score: number;
  db_id: number;
  arxiv_id: string;
  title: string;
  category: string;
  published_at: string;
  abstract: string;
  authors: string;
  arxiv_url: string;
}

interface RAGResponse {
  query: string;
  answer: string;
  sources: Source[];
}

export default function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedPaper, setSelectedPaper] = useState<Source | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(`http://127.0.0.1:8000/api/rag?q=${encodeURIComponent(query)}&limit=5`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: RAGResponse = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground p-4 md:p-10 font-sans selection:bg-primary selection:text-primary-foreground">
      <div className="max-w-5xl mx-auto space-y-10">

        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center space-y-3 pt-10"
        >
          <h1 className="text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-primary to-accent">
            PaperVault
          </h1>
          <p className="text-xl text-muted-foreground font-light">Enterprise Research Intelligence</p>
        </motion.div>

        {/* Search Engine */}
        <motion.form
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          onSubmit={handleSearch}
          className="relative group w-full max-w-3xl mx-auto"
        >
          <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-muted-foreground group-focus-within:text-primary transition-colors">
            <Search size={24} />
          </div>
          <input
            type="text"
            placeholder="E.g., What are the latest advancements in MLOps architectures?"
            className="w-full rounded-xl border border-input bg-background/50 pl-14 pr-36 py-4 text-foreground backdrop-blur-sm focus:border-primary focus:outline-none focus:ring-1 focus:ring-primary transition-all shadow-xl"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />

          <LiquidButton
            type="submit"
            variant="default"
            className="absolute right-2 top-2 bottom-2 h-auto px-6 rounded-lg font-bold"
            disabled={loading || !query.trim()}
          >
            {loading ? 'Synthesizing...' : 'Synthesize'}
          </LiquidButton>
        </motion.form>

        {/* Error Handling */}
        {error && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="bg-destructive/10 border border-destructive/20 text-destructive px-4 py-3 rounded-xl max-w-3xl mx-auto shadow-lg">
            <span>{error}</span>
          </motion.div>
        )}

        {/* Custom Uiverse Loader */}
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex justify-center py-20">
            <div className="loader">
              <div className="circle"><div className="dot"></div><div className="outline"></div></div>
              <div className="circle"><div className="dot"></div><div className="outline"></div></div>
              <div className="circle"><div className="dot"></div><div className="outline"></div></div>
              <div className="circle"><div className="dot"></div><div className="outline"></div></div>
              <div className="circle"><div className="dot"></div><div className="outline"></div></div>
            </div>
          </motion.div>
        )}

        {/* Results Layout */}
        {result && !loading && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="grid grid-cols-1 lg:grid-cols-3 gap-8"
          >
            {/* Deep Summary Section */}
            <div className="lg:col-span-2 space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <FileText className="text-primary" />
                <h2 className="text-2xl font-bold">Intelligence Brief</h2>
              </div>
              <div className="rounded-xl bg-card shadow-2xl border border-border backdrop-blur-md">
                <div className="p-6 prose prose-invert max-w-none prose-a:text-accent hover:prose-a:text-primary prose-headings:text-foreground">
                  <ReactMarkdown>{result.answer}</ReactMarkdown>
                </div>
              </div>
            </div>

            {/* Citations Sidebar */}
            <div className="space-y-4">
              <div className="flex items-center gap-2 mb-4">
                <h3 className="text-xl font-bold text-foreground">Sourced Literature</h3>
              </div>
              <div className="flex flex-col gap-3">
                {result.sources.map((source) => (
                  <motion.div
                    layoutId={`paper-modal-${source.db_id}`}
                    key={source.db_id}
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    onClick={() => setSelectedPaper(source)}
                    className="rounded-xl bg-card cursor-pointer shadow-md hover:border-primary border border-border transition-colors overflow-hidden"
                  >
                    <div className="p-5">
                      <div className="flex justify-between items-center mb-2">
                        <span className="border border-primary text-primary bg-primary/10 px-2 py-0.5 rounded text-xs font-mono">
                          {source.category}
                        </span>
                        {/* THE MISSING MATCH PERCENTAGE */}
                        <span className="text-xs text-muted-foreground font-mono bg-muted/50 px-2 py-0.5 rounded">
                          Match: {(source.score * 100).toFixed(1)}%
                        </span>
                      </div>
                      <h4 className="font-semibold text-sm leading-snug line-clamp-2 text-foreground mt-2">{source.title}</h4>
                      <div className="flex items-center gap-1 mt-3 text-xs text-muted-foreground">
                        <User size={12} /> <span className="truncate">{source.authors}</span>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>
        )}
      </div>

      {/* Elegant SaaS Modal for Paper Details */}
      <AnimatePresence>
        {selectedPaper && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedPaper(null)}
              className="absolute inset-0 bg-background/80 backdrop-blur-sm"
            />

            {/* Modal Content */}
            <motion.div
              layoutId={`paper-modal-${selectedPaper.db_id}`}
              className="relative w-full max-w-2xl bg-background rounded-2xl shadow-2xl border border-border overflow-hidden flex flex-col max-h-[85vh] z-10"
            >
              <div className="p-6 border-b border-border flex justify-between items-start bg-muted/30">
                <div className="space-y-3 pr-8">
                  <div className="flex gap-2">
                    <span className="bg-accent text-accent-foreground px-2 py-0.5 rounded text-xs font-mono">{selectedPaper.category}</span>
                    <span className="bg-secondary text-secondary-foreground px-2 py-0.5 rounded text-xs flex items-center gap-1"><Calendar size={12} /> {selectedPaper.published_at.split('T')[0]}</span>
                  </div>
                  <h3 className="text-xl font-bold leading-tight text-foreground">{selectedPaper.title}</h3>
                  <p className="text-sm text-muted-foreground flex items-center gap-1"><User size={14} /> {selectedPaper.authors}</p>
                </div>
                <button onClick={() => setSelectedPaper(null)} className="p-2 hover:bg-muted text-muted-foreground hover:text-foreground rounded-md transition-colors absolute right-4 top-4">
                  <X size={20} />
                </button>
              </div>

              <div className="p-6 overflow-y-auto custom-scrollbar">
                <h4 className="font-semibold mb-2 flex items-center gap-2 text-foreground">Abstract</h4>
                <p className="text-sm leading-relaxed text-muted-foreground">{selectedPaper.abstract || "Abstract not available in standard payload."}</p>
              </div>

              <div className="p-4 bg-muted/30 border-t border-border flex justify-end gap-3 mt-auto">
                <button onClick={() => setSelectedPaper(null)} className="px-4 py-2 rounded-md hover:bg-muted text-foreground text-sm font-medium transition-colors">Close</button>
                <a
                  href={selectedPaper.arxiv_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 px-4 py-2 rounded-md bg-primary text-primary-foreground text-sm font-medium hover:opacity-90 transition-opacity"
                >
                  Read on arXiv <ExternalLink size={16} />
                </a>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}