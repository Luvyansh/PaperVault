import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Search, FileText, ExternalLink, User, Calendar, X, BookOpen, Layers, Zap } from 'lucide-react';

import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import 'katex/dist/katex.min.css';

import { AnimatedThemeToggler } from '@/components/ui/animated-theme-toggler';
import { InteractiveHoverButton } from '@/components/ui/interactive-hover-button';
import { NeonGradientCard } from '@/components/ui/neon-gradient-card';
import { SplashIntro } from '@/components/splash-intro';

function shouldShowSplash(): boolean {
  try {
    return sessionStorage.getItem('papervault-splash-seen') !== '1';
  } catch {
    return true;
  }
}

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
  thinking?: string | null;
  sources: Source[];
}

const THINKING_PREF_KEY = 'papervault-show-thinking';

// ─── Synthesis Loader ─────────────────────────────────────────────────────────

const SynthesisLoader = () => (
  <motion.div
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    className="flex flex-col items-center gap-4 py-16"
  >
    <motion.div className="flex items-center gap-2">
      {[0, 1, 2].map((i) => (
        <motion.span
          key={i}
          className="h-2 w-2 rounded-full bg-primary"
          animate={{ opacity: [0.25, 1, 0.25], scale: [0.85, 1, 0.85] }}
          transition={{ duration: 1.1, repeat: Infinity, delay: i * 0.18, ease: 'easeInOut' }}
        />
      ))}
    </motion.div>
    <p className="text-sm text-base-content/45 font-mono tracking-wide">Synthesizing…</p>
  </motion.div>
);

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

    <motion.form
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2 }}
      onSubmit={onSearch}
      className="flex w-full max-w-2xl flex-col gap-3 sm:flex-row sm:items-stretch"
    >
      <div className="relative group flex-1">
        <motion.div className="absolute inset-y-0 left-5 flex items-center pointer-events-none text-base-content/30 group-focus-within:text-primary transition-colors duration-200">
          <Search size={22} />
        </motion.div>
        <input
          type="text"
          placeholder="E.g., What are the scaling laws for self-attention?"
          className="input w-full pl-14 py-5 h-auto text-base rounded-2xl bg-base-200 border border-base-300 text-base-content placeholder:text-base-content/25 focus:outline-none focus:border-primary shadow-xl transition-colors"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          disabled={loading}
          autoFocus
        />
      </div>
      <InteractiveHoverButton
        type="submit"
        disabled={loading || !query.trim()}
        className="shrink-0 rounded-2xl border-base-300 px-8 py-4 text-sm disabled:opacity-50 disabled:pointer-events-none sm:self-stretch"
      >
        {loading ? 'Searching...' : 'Synthesize'}
      </InteractiveHoverButton>
    </motion.form>

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
          className="cursor-default"
        >
          <NeonGradientCard
            borderSize={2}
            borderRadius={16}
            neonColors={{
              firstColor: 'var(--color-primary)',
              secondColor: 'var(--color-secondary)',
            }}
          >
            <Icon className="text-primary mb-3" size={20} />
            <h3 className="font-semibold text-sm text-base-content mb-1">{title}</h3>
            <p className="text-xs text-base-content/45 leading-relaxed">{desc}</p>
          </NeonGradientCard>
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
  const [splashDone, setSplashDone] = useState(() => !shouldShowSplash());
  const [showThinking, setShowThinking] = useState(() => {
    try {
      return localStorage.getItem(THINKING_PREF_KEY) === '1';
    } catch {
      return false;
    }
  });
  const [thinkingExpanded, setThinkingExpanded] = useState(true);

  const handleThinkingToggle = (enabled: boolean) => {
    setShowThinking(enabled);
    try {
      localStorage.setItem(THINKING_PREF_KEY, enabled ? '1' : '0');
    } catch {
      /* ignore */
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    setHasSearched(true);
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const params = new URLSearchParams({
        q: query,
        limit: '5',
        think: showThinking ? 'true' : 'false',
      });
      const res = await fetch(`http://127.0.0.1:8000/api/rag?${params}`);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data: RAGResponse = await res.json();
      setResult(data);
      if (data.thinking) setThinkingExpanded(true);
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
      <AnimatePresence>
        {!splashDone && <SplashIntro key="splash" onComplete={() => setSplashDone(true)} />}
      </AnimatePresence>

      <motion.div
        className="max-w-5xl mx-auto px-4 md:px-8"
        initial={{ opacity: 0, y: 10 }}
        animate={splashDone ? { opacity: 1, y: 0 } : { opacity: 0, y: 10 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      >
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
              <form
                onSubmit={handleSearch}
                className="flex w-full max-w-3xl flex-col gap-3 sm:flex-row sm:items-center"
              >
                <div className="relative group flex-1">
                  <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none text-base-content/30 group-focus-within:text-primary transition-colors duration-200">
                    <Search size={20} />
                  </div>
                  <input
                    type="text"
                    placeholder="Ask another research question..."
                    className="input w-full pl-12 h-14 rounded-xl bg-base-200 border border-base-300 text-base-content placeholder:text-base-content/25 focus:outline-none focus:border-primary transition-colors"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    disabled={loading}
                  />
                </div>
                <InteractiveHoverButton
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="shrink-0 rounded-xl border-base-300 px-6 py-3 text-sm disabled:opacity-50 disabled:pointer-events-none"
                >
                  {loading ? 'Searching...' : 'Synthesize'}
                </InteractiveHoverButton>
              </form>

              {error && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="alert alert-error max-w-3xl shadow-md"
                >
                  <span>{error}</span>
                </motion.div>
              )}

              <AnimatePresence>{loading && <SynthesisLoader />}</AnimatePresence>

              {result && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="grid grid-cols-1 lg:grid-cols-3 gap-8"
                >
                  <div className="lg:col-span-2 space-y-4">
                    <div className="flex flex-wrap items-center justify-between gap-3">
                      <div className="flex items-center gap-2">
                        <FileText className="text-primary" size={18} />
                        <h2 className="text-xl font-bold text-base-content">Intelligence Brief</h2>
                      </div>
                      <label className="flex items-center gap-2 cursor-pointer select-none text-sm text-base-content/60">
                        <input
                          type="checkbox"
                          className="toggle toggle-sm toggle-primary"
                          checked={showThinking}
                          onChange={(e) => handleThinkingToggle(e.target.checked)}
                        />
                        Show reasoning
                      </label>
                    </div>

                    {showThinking && result.thinking && (
                      <div className="rounded-2xl border border-base-300 bg-base-300/20 overflow-hidden">
                        <button
                          type="button"
                          onClick={() => setThinkingExpanded((v) => !v)}
                          className="w-full flex items-center justify-between px-4 py-3 text-left text-sm font-medium text-base-content/70 hover:bg-base-300/30 transition-colors"
                        >
                          <span>Model reasoning</span>
                          <span className="text-xs font-mono opacity-50">
                            {thinkingExpanded ? 'Hide' : 'Show'}
                          </span>
                        </button>
                        {thinkingExpanded && (
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="px-4 pb-4 prose prose-sm max-w-none text-base-content/55 border-t border-base-300/50"
                          >
                            <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                              {result.thinking}
                            </ReactMarkdown>
                          </motion.div>
                        )}
                      </div>
                    )}

                    {showThinking && !result.thinking && (
                      <p className="text-xs text-base-content/40 font-mono">
                        No reasoning trace returned. Your Ollama build must support think=true for this
                        model (e.g. gemma4:4b-thinking).
                      </p>
                    )}

                    <div className="rounded-2xl bg-base-200 border border-base-300 shadow-xl">
                      <div className="p-6 prose prose-sm max-w-none text-base-content prose-headings:text-base-content prose-a:text-primary prose-strong:text-base-content prose-code:text-secondary">
                        <ReactMarkdown remarkPlugins={[remarkMath]} rehypePlugins={[rehypeKatex]}>
                          {result.answer}
                        </ReactMarkdown>
                      </div>
                    </div>
                  </div>

                  <motion.div className="space-y-4">
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
                  </motion.div>
                </motion.div>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      <AnimatePresence>
        {selectedPaper && (
          <motion.div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedPaper(null)}
              className="absolute inset-0 bg-base-100/80 backdrop-blur-sm"
            />

            <motion.div
              layoutId={`paper-card-${selectedPaper.db_id}`}
              className="relative w-full max-w-2xl bg-base-200 rounded-3xl shadow-2xl border border-base-300 overflow-hidden flex flex-col max-h-[88vh] z-10"
            >
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

              <div className="p-4 border-t border-base-300 bg-base-300/30 flex justify-end gap-3">
                <button onClick={() => setSelectedPaper(null)} className="btn btn-ghost btn-sm">
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
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
