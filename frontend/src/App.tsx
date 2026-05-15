import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Search, FileText, ExternalLink, User, Calendar, X, BookOpen, Layers, Zap } from 'lucide-react';

import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

import { LiquidButton } from '@/components/animate-ui/components/buttons/liquid';
import { AnimatedThemeToggler } from '@/components/ui/animated-theme-toggler';

// ─── Types ────────────────────────────────────────────────────────────────────

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

// ─── Synthesis Loader ─────────────────────────────────────────────────────────

const LOADER_STEPS = [
  'Scanning arXiv corpus...',
  'Ranking by semantic relevance...',
  'Synthesizing intelligence brief...',
];

const SynthesisLoader = () => {
  const [stepIdx, setStepIdx] = useState(0);

  useEffect(() => {
    const timer = setInterval(() => setStepIdx((s) => (s + 1) % LOADER_STEPS.length), 1800);
    return () => clearInterval(timer);
  }, []);

  const nodes = Array.from({ length: 6 }, (_, i) => ({
    angle: (i * 60 * Math.PI) / 180,
    delay: i * 0.22,
  }));

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="flex flex-col items-center gap-10 py-20"
    >
      {/* Animated knowledge-graph */}
      <div className="relative w-44 h-44">
        {/* Outer rotating ring */}
        <motion.div
          className="absolute inset-0 rounded-full border-2 border-transparent"
          style={{
            borderTopColor: 'var(--color-primary)',
            borderRightColor: 'var(--color-primary)',
          }}
          animate={{ rotate: 360 }}
          transition={{ duration: 3, repeat: Infinity, ease: 'linear' }}
        />
        {/* Inner counter-rotating ring */}
        <motion.div
          className="absolute inset-5 rounded-full border-2 border-transparent"
          style={{
            borderBottomColor: 'var(--color-accent)',
            borderLeftColor: 'var(--color-accent)',
          }}
          animate={{ rotate: -360 }}
          transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
        />

        {/* SVG connection lines */}
        <svg className="absolute inset-0 w-full h-full" viewBox="0 0 176 176">
          {nodes.map((node, i) => (
            <motion.line
              key={i}
              x1="88"
              y1="88"
              x2={88 + Math.cos(node.angle) * 60}
              y2={88 + Math.sin(node.angle) * 60}
              strokeWidth="1"
              strokeDasharray="4 4"
              style={{ stroke: 'var(--color-primary)' }}
              initial={{ opacity: 0 }}
              animate={{ opacity: [0, 0.45, 0.45, 0] }}
              transition={{
                duration: 2.4,
                delay: node.delay,
                repeat: Infinity,
                repeatDelay: 0.4,
                ease: 'easeInOut',
              }}
            />
          ))}
        </svg>

        {/* Satellite nodes */}
        {nodes.map((node, i) => (
          <motion.div
            key={i}
            className="absolute w-3 h-3 rounded-full bg-secondary"
            style={{ top: '50%', left: '50%', marginTop: -6, marginLeft: -6 }}
            initial={{ opacity: 0, x: 0, y: 0 }}
            animate={{
              opacity: [0, 1, 1, 0],
              x: Math.cos(node.angle) * 60,
              y: Math.sin(node.angle) * 60,
              scale: [0.4, 1, 1, 0.4],
            }}
            transition={{
              duration: 2.4,
              delay: node.delay,
              repeat: Infinity,
              repeatDelay: 0.4,
              ease: 'easeInOut',
            }}
          />
        ))}

        {/* Pulsing center dot */}
        <motion.div
          className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-primary"
          animate={{ scale: [1, 1.3, 1], opacity: [0.55, 1, 0.55] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>

      {/* Cycling status text */}
      <AnimatePresence mode="wait">
        <motion.p
          key={stepIdx}
          initial={{ opacity: 0, y: 8 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -8 }}
          transition={{ duration: 0.3 }}
          className="text-sm font-mono tracking-widest text-base-content/40 uppercase"
        >
          {LOADER_STEPS[stepIdx]}
        </motion.p>
      </AnimatePresence>
    </motion.div>
  );
};

// ─── Landing Hero ─────────────────────────────────────────────────────────────

const FEATURES = [
  {
    icon: BookOpen,
    title: 'Deep Research',
    desc: 'Pulls from thousands of arXiv papers using semantic vector search.',
  },
  {
    icon: Layers,
    title: 'Cited Synthesis',
    desc: 'Every insight is grounded with precise paper-level citations.',
  },
  {
    icon: Zap,
    title: 'Instant Brief',
    desc: 'Get a research-grade intelligence summary in seconds.',
  },
];

const LandingHero = ({
  query,
  setQuery,
  onSearch,
  loading,
}: {
  query: string;
  setQuery: (q: string) => void;
  onSearch: (e: React.FormEvent) => void;
  loading: boolean;
}) => (
  <motion.div
    key="landing"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0, y: -20 }}
    className="flex flex-col items-center justify-center gap-12 min-h-[82vh] pt-6 pb-20"
  >
    {/* Badge */}
    <motion.div
      initial={{ opacity: 0, y: -10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.05 }}
    >
      <span className="inline-flex items-center gap-2 bg-primary/10 text-primary border border-primary/25 rounded-full px-4 py-1.5 text-xs font-mono tracking-wider uppercase">
        <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" />
        RAG · arXiv · Semantic Search
      </span>
    </motion.div>

    {/* Title */}
    <motion.div
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1 }}
      className="text-center space-y-5"
    >
      <h1 className="text-8xl md:text-9xl font-black tracking-tighter leading-none text-base-content">
        Paper<span className="text-primary">Vault</span>
      </h1>
      <p className="text-lg text-base-content/50 font-light max-w-sm mx-auto leading-relaxed">
        Ask any research question. Get a synthesis of the latest papers — cited, grounded, and clear.
      </p>
    </motion.div>

    {/* Search bar */}
    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      onSubmit={onSearch}
      className="relative group w-full max-w-2xl"
    >
      <div className="absolute inset-y-0 left-5 flex items-center pointer-events-none text-base-content/30 group-focus-within:text-primary transition-colors duration-200">
        <Search size={22} />
      </div>
      <input
        type="text"
        placeholder="E.g., What are the scaling laws for self-attention?"
        className="input w-full pl-14 pr-44 py-5 h-auto text-base rounded-2xl bg-base-200 border border-base-300 text-base-content placeholder:text-base-content/25 focus:outline-none focus:border-primary shadow-xl transition-colors"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        disabled={loading}
        autoFocus
      />
      <div className="absolute right-2 top-2 bottom-2 flex items-stretch">
        <LiquidButton
          type="submit"
          variant="default"
          className="h-full px-6 rounded-xl font-bold text-sm"
          disabled={loading || !query.trim()}
        >
          {loading ? 'Searching...' : 'Synthesize'}
        </LiquidButton>
      </div>
    </motion.form>

    {/* Feature cards */}
    <motion.div
      initial={{ opacity: 0, y: 30 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.32 }}
      className="grid grid-cols-1 md:grid-cols-3 gap-4 w-full max-w-2xl"
    >
      {FEATURES.map(({ icon: Icon, title, desc }, i) => (
        <motion.div
          key={title}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.38 + i * 0.07 }}
          className="bg-base-200 rounded-2xl p-5 border border-base-300 hover:border-primary/50 transition-colors duration-200 cursor-default"
        >
          <Icon className="text-primary mb-3" size={20} />
          <h3 className="font-semibold text-sm text-base-content mb-1">{title}</h3>
          <p className="text-xs text-base-content/45 leading-relaxed">{desc}</p>
        </motion.div>
      ))}
    </motion.div>
  </motion.div>
);

// ─── Main App ─────────────────────────────────────────────────────────────────

export default function App() {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<RAGResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [selectedPaper, setSelectedPaper] = useState<Source | null>(null);
  const [hasSearched, setHasSearched] = useState(false);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setHasSearched(true);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const res = await fetch(
        `http://127.0.0.1:8000/api/rag?q=${encodeURIComponent(query)}&limit=5`
      );
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: RAGResponse = await res.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unknown error occurred.');
    } finally {
      setLoading(false);
    }
  };

  const resetToLanding = () => {
    setHasSearched(false);
    setResult(null);
    setError(null);
    setQuery('');
  };

  return (
    <div className="min-h-screen bg-base-100 text-base-content font-sans">
      <div className="max-w-5xl mx-auto px-4 md:px-8">

        {/* ── Navbar ─────────────────────────────────────────────────── */}
        <header className="flex items-center justify-between py-5">
          <button
            onClick={resetToLanding}
            className="text-lg font-black tracking-tight text-base-content hover:text-primary transition-colors duration-200"
          >
            Paper<span className="text-primary">Vault</span>
          </button>
          <AnimatedThemeToggler
            mode="daisyui"
            lightTheme="fantasy"
            darkTheme="forest"
            className="btn btn-ghost btn-circle text-base-content hover:bg-base-200 [&_svg]:size-5"
            title="Toggle theme"
          />
        </header>

        {/* ── Page content ────────────────────────────────────────────── */}
        <AnimatePresence mode="wait">
          {!hasSearched ? (
            <LandingHero
              query={query}
              setQuery={setQuery}
              onSearch={handleSearch}
              loading={loading}
            />
          ) : (
            <motion.div
              key="results"
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0 }}
              className="space-y-8 pb-20"
            >
              {/* Compact search bar */}
              <form onSubmit={handleSearch} className="relative group w-full max-w-3xl">
                <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-base-content/30 group-focus-within:text-primary transition-colors duration-200">
                  <Search size={20} />
                </div>
                <input
                  type="text"
                  placeholder="Ask another research question..."
                  className="input w-full pl-12 pr-40 h-14 rounded-xl bg-base-200 border border-base-300 text-base-content placeholder:text-base-content/25 focus:outline-none focus:border-primary transition-colors"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  disabled={loading}
                />
                <div className="absolute right-2 top-2 bottom-2 flex items-stretch">
                  <LiquidButton
                    type="submit"
                    variant="default"
                    className="h-full px-5 rounded-lg font-bold text-sm"
                    disabled={loading || !query.trim()}
                  >
                    {loading ? 'Searching...' : 'Synthesize'}
                  </LiquidButton>
                </div>
              </form>

              {/* Error state */}
              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="alert alert-error max-w-3xl shadow-md"
                >
                  <span>{error}</span>
                </motion.div>
              )}

              {/* Synthesis Loader */}
              <AnimatePresence>{loading && <SynthesisLoader />}</AnimatePresence>

              {/* Results grid */}
              {result && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="grid grid-cols-1 lg:grid-cols-3 gap-8"
                >
                  {/* ── Intelligence Brief ─────────────────────────── */}
                  <div className="lg:col-span-2 space-y-4">
                    <div className="flex items-center gap-2">
                      <FileText className="text-primary" size={18} />
                      <h2 className="text-xl font-bold text-base-content">Intelligence Brief</h2>
                    </div>
                    <div className="rounded-2xl bg-base-200 border border-base-300 shadow-xl">
                      <div className="p-6 prose prose-sm max-w-none text-base-content prose-headings:text-base-content prose-a:text-primary prose-strong:text-base-content prose-code:text-secondary">
                        <ReactMarkdown
                          remarkPlugins={[remarkMath]}
                          rehypePlugins={[rehypeKatex]}
                        >
                          {result.answer}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>

                  {/* ── Citations Sidebar ───────────────────────────── */}
                  <div className="space-y-4">
                    <h3 className="text-lg font-bold text-base-content">Sourced Literature</h3>
                    <div className="flex flex-col gap-3">
                      {result.sources.map((source) => (
                        <motion.div
                          layoutId={`paper-card-${source.db_id}`}
                          key={source.db_id}
                          whileHover={{ scale: 1.02 }}
                          whileTap={{ scale: 0.97 }}
                          onClick={() => setSelectedPaper(source)}
                          className="rounded-2xl bg-base-200 border border-base-300 hover:border-primary cursor-pointer transition-colors duration-200 shadow-md overflow-hidden"
                        >
                          <div className="p-4 space-y-2">
                            <div className="flex items-center justify-between">
                              <span className="badge badge-outline badge-sm font-mono text-primary border-primary/40 bg-primary/5">
                                {source.category}
                              </span>
                              <span className="text-xs text-base-content/35 font-mono">
                                {(source.score * 100).toFixed(1)}%
                              </span>
                            </div>
                            <h4 className="text-sm font-semibold leading-snug line-clamp-2 text-base-content">
                              {source.title}
                            </h4>
                            <div className="flex items-center gap-1 text-xs text-base-content/40">
                              <User size={11} />
                              <span className="truncate">{source.authors}</span>
                            </div>
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* ── Paper Detail Modal ───────────────────────────────────────── */}
      <AnimatePresence>
        {selectedPaper && (
          <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedPaper(null)}
              className="absolute inset-0 bg-base-100/80 backdrop-blur-sm"
            />

            {/* Modal */}
            <motion.div
              layoutId={`paper-card-${selectedPaper.db_id}`}
              className="relative w-full max-w-2xl bg-base-200 rounded-3xl shadow-2xl border border-base-300 overflow-hidden flex flex-col max-h-[88vh] z-10"
            >
              {/* Header */}
              <div className="p-6 border-b border-base-300 bg-base-300/30 flex justify-between items-start">
                <div className="space-y-3 pr-10">
                  <div className="flex gap-2 flex-wrap">
                    <span className="badge badge-accent font-mono text-xs">
                      {selectedPaper.category}
                    </span>
                    <span className="badge badge-ghost text-xs flex items-center gap-1">
                      <Calendar size={11} />
                      {selectedPaper.published_at.split('T')[0]}
                    </span>
                  </div>
                  <h3 className="text-lg font-bold text-base-content leading-snug">
                    {selectedPaper.title}
                  </h3>
                  <p className="text-sm text-base-content/50 flex items-center gap-1.5">
                    <User size={13} />
                    {selectedPaper.authors}
                  </p>
                </div>
                <button
                  onClick={() => setSelectedPaper(null)}
                  className="btn btn-ghost btn-sm btn-circle absolute right-4 top-4 text-base-content/50 hover:text-base-content"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Abstract body */}
              <div className="p-6 overflow-y-auto custom-scrollbar flex-1">
                <h4 className="text-sm font-semibold text-base-content mb-3 uppercase tracking-wider opacity-60">
                  Abstract
                </h4>
                <div className="prose prose-sm max-w-none text-base-content/60 prose-headings:text-base-content prose-strong:text-base-content/80">
                  <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                    {selectedPaper.abstract || 'Abstract not available.'}
                  </ReactMarkdown>
                </div>
              </div>

              {/* Footer */}
              <div className="p-4 border-t border-base-300 bg-base-300/30 flex justify-end gap-3">
                <button
                  onClick={() => setSelectedPaper(null)}
                  className="btn btn-ghost btn-sm"
                >
                  Close
                </button>
                <a
                  href={selectedPaper.arxiv_url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="btn btn-primary btn-sm gap-2"
                >
                  Read on arXiv <ExternalLink size={14} />
                </a>
              </div>
            </motion.div>
          </div>
        )}
      </AnimatePresence>
    </div>
  );
}