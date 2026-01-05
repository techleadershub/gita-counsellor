import { useState, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import ResearchProgress from './components/ResearchProgress';
import {
  BookOpen,
  Github,
  Sparkles,
  Compass,
  Flower2,
  ScrollText,
  Send,
  Search,
  MessageCircle,
  Feather,
  Brain,
  Info,
  Menu,
  X,
  ExternalLink,
  Target
} from 'lucide-react';

function App() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => {
      setScrolled(window.scrollY > 20);
    };
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return (
    <div className="min-h-screen bg-starlight-50 selection:bg-nebula-200 selection:text-nebula-900 font-sans">
      <div className={`fixed inset-0 bg-[#f8fafc] -z-20`}></div>
      {/* Mesh Gradient Background */}
      <div className="fixed inset-0 -z-10 opacity-60" style={{
        backgroundImage: `
          radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%), 
          radial-gradient(at 100% 0%, rgba(245, 158, 11, 0.1) 0px, transparent 50%)`
      }}></div>

      <nav className={`fixed w-full z-50 transition-all duration-300 ${scrolled ? 'glass-nav py-2.5 sm:py-3' : 'bg-transparent py-3 sm:py-5'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            {/* Logo Section */}
            <div className="flex items-center gap-2 sm:gap-3">
              <div className="w-8 h-8 sm:w-10 sm:h-10 bg-gradient-to-br from-nebula-500/10 to-nebula-500/5 rounded-xl flex items-center justify-center border border-nebula-100 shadow-sm transform rotate-0 group transition-all hover:scale-105">
                <img src="/logo.svg" alt="Gita Counsellor Logo" className="w-6 h-6 sm:w-8 sm:h-8 drop-shadow-sm" />
              </div>
              <div className="flex flex-col">
                <h1 className="text-lg sm:text-2xl font-bold text-gray-900 tracking-tight font-sans leading-none">Gita Counsellor</h1>
                <span className="text-[9px] sm:text-[10px] text-nebula-600 font-bold tracking-[0.2em] uppercase mt-0.5 sm:mt-1 hidden sm:block">The Life Manual</span>
              </div>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden sm:flex items-center gap-4">
              <button
                onClick={() => window.location.reload()}
                className="text-sm font-medium text-gray-600 hover:text-nebula-600 transition-colors"
              >
                New Chat
              </button>
              <a href="https://ramayanacounsellor.futureproofindia.com/" target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-nebula-600 transition-colors px-4 py-2 rounded-full hover:bg-starlight-100/50">
                <ExternalLink className="w-4 h-4" />
                <span>Ramayana Counsellor</span>
              </a>
              <a href="https://github.com/techleadershub/gita-counsellor" target="_blank" rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm font-medium text-gray-600 hover:text-nebula-600 transition-colors px-4 py-2 rounded-full hover:bg-starlight-100/50">
                <Github className="w-4 h-4 fill-current" />
                <span>About Project</span>
              </a>
            </div>

            {/* Mobile Hamburger Button */}
            <button
              className="sm:hidden p-2 text-gray-600 hover:text-nebula-600 transition-colors"
              onClick={() => setMobileMenuOpen(true)}
            >
              <Menu className="w-6 h-6" />
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-[60] sm:hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/20 backdrop-blur-sm animate-fade-in"
            onClick={() => setMobileMenuOpen(false)}
          />

          {/* Menu Drawer */}
          <div className="absolute right-0 top-0 bottom-0 w-[280px] bg-white shadow-2xl animate-slide-left p-6 flex flex-col">
            <div className="flex justify-between items-center mb-8">
              <h2 className="text-xl font-bold text-nebula-900 font-serif">Menu</h2>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors"
              >
                <X className="w-6 h-6" />
              </button>
            </div>

            <div className="space-y-6 flex-1">
              <button
                onClick={() => {
                  window.location.reload();
                  setMobileMenuOpen(false);
                }}
                className="flex items-center gap-3 text-lg font-medium text-gray-800 w-full p-2 rounded-lg hover:bg-starlight-50 active:bg-starlight-100 transition-colors"
              >
                <MessageCircle className="w-5 h-5 text-nebula-500" />
                New Chat
              </button>

              <a
                href="https://ramayanacounsellor.futureproofindia.com/"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 text-lg font-medium text-gray-800 w-full p-2 rounded-lg hover:bg-starlight-50 active:bg-starlight-100 transition-colors"
              >
                <ExternalLink className="w-5 h-5 text-nebula-500" />
                Ramayana Counsellor
              </a>

              <a
                href="https://github.com/techleadershub/gita-counsellor"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 text-lg font-medium text-gray-800 w-full p-2 rounded-lg hover:bg-starlight-50 active:bg-starlight-100 transition-colors"
              >
                <Github className="w-5 h-5 text-nebula-500" />
                About Project
              </a>

              <a
                href="https://www.linkedin.com/in/sridharjammalamadaka/"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-3 text-lg font-medium text-gray-800 w-full p-2 rounded-lg hover:bg-starlight-50 active:bg-starlight-100 transition-colors"
              >
                <Info className="w-5 h-5 text-nebula-500" />
                Developer
              </a>
            </div>

            <div className="pt-6 border-t border-gray-100">
              <p className="text-xs text-center text-gray-400">
                Gita Counsellor v1.0
                <br />
                The Life Manual
              </p>
            </div>
          </div>
        </div>
      )}

      <main className="relative z-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 sm:pt-32 pb-36 sm:pb-16">
        <ResearchView />
      </main>

      <footer className="relative border-t border-starlight-200 bg-starlight-100/50 mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8 flex flex-col sm:flex-row justify-center items-center gap-2 text-center">
          <p className="flex items-center gap-2 text-sm text-gray-500">
            <span>Powered by AI & Ancient Wisdom</span>
            <span className="hidden sm:inline w-1 h-1 rounded-full bg-gray-300"></span>
          </p>
          <a
            href="https://www.linkedin.com/in/sridharjammalamadaka/"
            target="_blank"
            rel="noopener noreferrer"
            className="text-sm font-medium text-nebula-600 hover:text-nebula-800 transition-colors flex items-center gap-1"
          >
            Built by Sridhar Jammalamadaka
          </a>
        </div>
      </footer>
    </div>
  );
}

function ResearchView() {
  const [query, setQuery] = useState('');
  const [context, setContext] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('analysis');
  const [showProgress, setShowProgress] = useState(false);
  const [currentQuery, setCurrentQuery] = useState('');

  const tabsContainerRef = useRef(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    setLoading(true);
    setError(null);
    setResult(null);
    setShowProgress(true);
    setCurrentQuery(query);
  };

  const handleProgressComplete = (data) => {
    setResult(data);
    setActiveTab('analysis');
    setShowProgress(false);
    setLoading(false);
  };

  const handleProgressError = (err) => {
    setError(err.message || 'Research failed');
    setShowProgress(false);
    setLoading(false);
  };

  const tabs = [
    { id: 'analysis', label: 'Deep Analysis', icon: Brain, color: 'text-blue-500', bg: 'bg-blue-50' },
    { id: 'guidance', label: 'Action Plan', icon: Target, color: 'text-emerald-500', bg: 'bg-emerald-50' },
    { id: 'exercises', label: 'Practices', icon: Flower2, color: 'text-rose-500', bg: 'bg-rose-50' },
    { id: 'verses', label: `Verses`, count: result?.verses?.length, icon: ScrollText, color: 'text-nebula-600', bg: 'bg-nebula-50' },
  ];

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Hero / Input Section */}
      <div className={`transition-all duration-700 ease-in-out ${result ? '' : 'max-w-3xl mx-auto mt-4 sm:mt-16'}`}>
        {!result && (
          <div className="text-center mb-8 sm:mb-12">
            <h2 className="text-3xl sm:text-5xl font-bold text-gray-900 mb-4 sm:mb-6 font-serif leading-tight">
              Seek Guidance from <br className="hidden sm:block" />
              <span className="relative inline-block mt-1 sm:mt-2">
                <span className="relative z-10 text-transparent bg-clip-text bg-gradient-to-r from-nebula-600 to-nebula-400">The Bhagavad Gita</span>
                <svg className="absolute -bottom-1 sm:-bottom-2 left-0 w-full h-2 sm:h-3 text-nebula-200 -z-10" viewBox="0 0 100 10" preserveAspectRatio="none">
                  <path d="M0 5 Q 50 10 100 5" stroke="currentColor" strokeWidth="8" fill="none" />
                </svg>
              </span>
            </h2>
            <p className="text-base sm:text-lg text-gray-600 max-w-2xl mx-auto leading-relaxed px-4 sm:px-0">
              Facing a dilemma? Describe your situation and receive personalized wisdom drawn from the eternal verses.
            </p>
          </div>
        )}

        <div className={`glass-panel rounded-2xl p-1 shadow-2xl shadow-nebula-100/50 transition-all ${result ? 'border-b-0' : ''}`}>
          <div className="bg-white rounded-xl border border-starlight-200 overflow-hidden">
            <form onSubmit={handleSubmit} className="p-1">
              <div className="space-y-1">
                <div className="relative group">
                  <div className="absolute top-4 sm:top-6 left-4 sm:left-5 text-gray-400 group-focus-within:text-nebula-500 transition-colors">
                    <Search className="w-5 h-5 sm:w-6 sm:h-6" />
                  </div>
                  <textarea
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="What is troubling you today?"
                    className="w-full pl-11 sm:pl-14 pr-4 sm:pr-5 py-3 sm:py-5 bg-transparent border-none focus:ring-0 text-lg sm:text-xl text-gray-800 placeholder-gray-300 resize-none font-serif leading-relaxed"
                    rows={result ? 1 : 2}
                    required
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSubmit(e);
                      }
                    }}
                  />
                </div>

                <div className={`${result ? 'hidden' : 'block'} border-t border-dashed border-gray-100 relative group animate-slide-up`}>
                  <div className="absolute top-4 left-5 text-gray-400 group-focus-within:text-nebula-500 transition-colors">
                    <MessageCircle className="w-5 h-5" />
                  </div>
                  <textarea
                    value={context}
                    onChange={(e) => setContext(e.target.value)}
                    placeholder="Add context (optional)..."
                    className="w-full pl-14 pr-5 py-4 bg-transparent border-none focus:ring-0 text-gray-600 placeholder-gray-300 resize-none"
                    rows={1}
                  />
                </div>
              </div>

              <div className="px-4 pb-4 flex justify-between items-center bg-starlight-50/30 rounded-b-lg">
                <div className="text-xs text-gray-400 hidden sm:block">
                  <span className="flex items-center gap-1"><Info className="w-3 h-3" /> Press Enter to search</span>
                </div>
                <button
                  type="submit"
                  disabled={loading || !query.trim()}
                  className="ml-auto group relative overflow-hidden rounded-xl bg-gradient-to-r from-nebula-600 to-nebula-500 px-6 py-2.5 text-white shadow-lg transition-all hover:shadow-nebula-500/30 hover:scale-[1.02] disabled:opacity-70 disabled:hover:scale-100"
                >
                  <span className="relative flex items-center justify-center gap-2 font-semibold tracking-wide text-sm">
                    {loading ? (
                      'Processing...'
                    ) : (
                      <>
                        Get Guidance
                        <Send className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                      </>
                    )}
                  </span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {showProgress && (
        <div className="max-w-3xl mx-auto animate-fade-in">
          <ResearchProgress
            query={currentQuery}
            context={context}
            onComplete={handleProgressComplete}
            onError={handleProgressError}
          />
        </div>
      )}

      {error && (
        <div className="max-w-3xl mx-auto bg-red-50 border border-red-100 rounded-xl p-6 text-center animate-fade-in flex flex-col items-center">
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mb-3">
            <span className="text-2xl">⚠️</span>
          </div>
          <p className="text-red-800 font-medium mb-2">{error}</p>
          <button onClick={() => setError(null)} className="text-sm text-red-600 hover:text-red-800 font-medium">Try Again</button>
        </div>
      )}

      {result && (<>
        <div className="animate-slide-up space-y-8">
          {/* Tabs Navigation */}
          {/* Tabs Navigation (Desktop) */}
          <div className="hidden sm:block sticky top-20 z-40 bg-starlight-50/95 backdrop-blur-md shadow-sm border-y border-starlight-200 rounded-2xl border px-2 py-2">
            <div
              ref={tabsContainerRef}
              className="flex justify-center gap-1 snap-x p-1"
            >
              {tabs.map((tab) => {
                const Icon = tab.icon;
                const isActive = activeTab === tab.id;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex-none snap-center flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm transition-all whitespace-nowrap ${isActive
                      ? 'bg-white text-nebula-700 shadow-md ring-1 ring-black/5'
                      : 'text-gray-500 hover:bg-white/50 hover:text-gray-900'
                      }`}
                  >
                    <Icon className={`w-4 h-4 ${isActive ? 'text-nebula-600' : 'text-gray-400'}`} />
                    <span>{tab.label}</span>
                    {tab.count !== undefined && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded-full ${isActive ? 'bg-nebula-100 text-nebula-700' : 'bg-starlight-200 text-gray-500'}`}>
                        {tab.count}
                      </span>
                    )}
                  </button>
                );
              })}
            </div>
          </div>



          {/* Content Area */}
          <div className="glass-panel rounded-3xl p-6 sm:p-12 min-h-[500px] relative overflow-hidden mb-24 sm:mb-0">
            {/* Background Texture */}
            <div className="absolute top-0 right-0 p-12 opacity-[0.02] pointer-events-none">
              <Flower2 className="w-96 h-96" />
            </div>

            {tabs.map((tab) => {
              if (activeTab !== tab.id) return null;
              const HeaderIcon = tab.icon;
              return (
                <div key={tab.id} className="animate-fade-in relative z-10">
                  <div className="flex items-center gap-4 mb-8 pb-8 border-b border-starlight-200">
                    <div className={`p-3 rounded-xl ${tab.bg}`}>
                      <HeaderIcon className={`w-8 h-8 ${tab.color}`} />
                    </div>
                    <div>
                      <h3 className="text-2xl font-bold text-gray-900 font-serif">{tab.label}</h3>
                      <p className="text-sm text-gray-500">Divine insight for your situation</p>
                    </div>
                  </div>

                  {/* Tab Content Rendered Below */
                    tab.id === 'analysis' && (
                      <div className="prose prose-saffron max-w-none sm:prose-lg">
                        <ReactMarkdown>{result.analysis}</ReactMarkdown>
                      </div>
                    )}
                  {tab.id === 'guidance' && (
                    <div className="prose prose-saffron max-w-none sm:prose-lg">
                      <ReactMarkdown>{result.guidance}</ReactMarkdown>
                    </div>
                  )}
                  {tab.id === 'exercises' && (
                    <div className="prose prose-saffron max-w-none sm:prose-lg">
                      {result.exercises && result.exercises.trim() ? (
                        <ReactMarkdown>{result.exercises}</ReactMarkdown>
                      ) : (
                        <div className="flex flex-col items-center justify-center py-20 text-center">
                          <div className="w-16 h-16 bg-starlight-100 rounded-full flex items-center justify-center mb-4 text-starlight-400">
                            <Flower2 className="w-8 h-8" />
                          </div>
                          <p className="text-gray-500 italic max-w-md">Reflect on the guidance provided in the main answer section to derive your own spiritual exercises.</p>
                        </div>
                      )}
                    </div>
                  )}
                  {tab.id === 'verses' && (
                    <div className="space-y-8">
                      {result.verses && result.verses.length > 0 ? (
                        result.verses.map((verse, idx) => (
                          <div key={idx} className="group relative bg-white border border-starlight-200 rounded-2xl p-6 sm:p-8 hover:shadow-xl hover:border-nebula-300 transition-all duration-300">
                            <div className="flex flex-col sm:flex-row sm:items-baseline justify-between mb-6 pb-4 border-b border-starlight-100 gap-2">
                              <h4 className="text-xl font-bold font-serif text-nebula-800 tracking-tight">{verse.verse_id}</h4>
                              <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold bg-starlight-100 text-nebula-800 uppercase tracking-widest border border-starlight-200">
                                <ScrollText className="w-3 h-3" />
                                Chapter {verse.chapter} • Verse {verse.verse_number}
                              </span>
                            </div>

                            {verse.transliteration && (
                              <div className="mb-6 bg-starlight-50/50 p-6 rounded-xl border-l-4 border-nebula-400">
                                <p className="text-lg text-gray-800 font-serif italic text-center leading-loose">{verse.transliteration}</p>
                              </div>
                            )}

                            <div className="grid gap-6">
                              {verse.word_meanings && (
                                <div className="text-sm text-gray-600 bg-starlight-50/30 p-4 rounded-lg border border-starlight-100">
                                  <span className="font-bold text-nebula-700 block mb-2 uppercase text-xs tracking-wider">Word Meanings</span>
                                  <div className="leading-relaxed">{verse.word_meanings}</div>
                                </div>
                              )}

                              {verse.translation && (
                                <div>
                                  <span className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-3">Translation</span>
                                  <blockquote className="text-xl text-gray-900 font-serif leading-relaxed border-l-2 border-nebula-200 pl-4">
                                    "{verse.translation}"
                                  </blockquote>
                                </div>
                              )}

                              {verse.purport && (
                                <div className="pt-4 border-t border-starlight-100">
                                  <span className="text-xs font-bold text-gray-400 uppercase tracking-widest block mb-3">Purport</span>
                                  <div className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                                    {verse.purport}
                                  </div>
                                </div>
                              )}
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-20">
                          <p className="text-gray-500 text-lg">No direct verses were cited for this query.</p>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Mobile Bottom Navigation */}
        <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-starlight-200 pb-safe sm:hidden">
          <div className="flex justify-around items-center h-[72px] px-1 pb-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              const isActive = activeTab === tab.id;
              // Shorten labels for mobile
              const mobileLabel = {
                'Divine Guidance': 'Guidance',
                'Deep Analysis': 'Analysis',
                'Action Plan': 'Action',
                'Practices': 'Practice',
                'Verses': 'Verses'
              }[tab.label] || tab.label;

              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`flex flex-col items-center justify-center w-full h-full space-y-1 transition-all active:scale-95 ${isActive ? 'text-nebula-600' : 'text-gray-400'
                    }`}
                >
                  <div className={`p-1.5 rounded-2xl transition-all ${isActive ? 'bg-nebula-100/50' : 'bg-transparent'}`}>
                    <Icon className={`w-6 h-6 ${isActive ? 'stroke-nebula-600' : ''}`} strokeWidth={isActive ? 2 : 1.5} />
                  </div>
                  <span className="text-[10px] font-medium tracking-tight leading-none">
                    {mobileLabel}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      </>)}
    </div>
  );
}

export default App;
