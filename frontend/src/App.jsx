import { useState } from 'react';
import ReactMarkdown from 'react-markdown';
import { research } from './api';

function App() {

  return (
    <div className="min-h-screen bg-gradient-to-br from-saffron-50 to-orange-100">
      <nav className="bg-saffron-600 text-white shadow-lg sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <h1 className="text-2xl font-bold">🕉️ Bhagavad Gita Research Agent</h1>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ResearchView />
      </main>
    </div>
  );
}

function ResearchView() {
  const [query, setQuery] = useState('');
  const [context, setContext] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('answer');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const data = await research(query, context || null);
      setResult(data);
      setActiveTab('answer');
    } catch (err) {
      setError(err.response?.data?.detail || err.message || 'Failed to get research results');
      console.error('Research error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-xl shadow-lg p-6">
        <h2 className="text-3xl font-bold text-gray-800 mb-4">Ask Your Question</h2>
        <p className="text-gray-600 mb-6">
          Get comprehensive guidance from Bhagavad Gita for your modern problems and questions.
        </p>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Question or Problem *
            </label>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="e.g., I'm feeling stressed about my career decisions. What should I do?"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saffron-500 focus:border-transparent resize-none"
              rows={4}
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Additional Context (Optional)
            </label>
            <textarea
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="Provide any additional context about your situation..."
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saffron-500 focus:border-transparent resize-none"
              rows={3}
            />
          </div>

          <button
            type="submit"
            disabled={loading || !query.trim()}
            className="w-full bg-saffron-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-saffron-700 disabled:opacity-50 disabled:cursor-not-allowed transition"
          >
            {loading ? 'Researching...' : 'Get Guidance from Bhagavad Gita'}
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {result && (
        <div className="bg-white rounded-xl shadow-lg overflow-hidden">
          <div className="border-b border-gray-200">
            <div className="flex">
              <button
                onClick={() => setActiveTab('answer')}
                className={`flex-1 px-6 py-4 font-semibold transition ${
                  activeTab === 'answer'
                    ? 'bg-saffron-50 text-saffron-700 border-b-2 border-saffron-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Complete Answer
              </button>
              <button
                onClick={() => setActiveTab('analysis')}
                className={`flex-1 px-6 py-4 font-semibold transition ${
                  activeTab === 'analysis'
                    ? 'bg-saffron-50 text-saffron-700 border-b-2 border-saffron-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Analysis
              </button>
              <button
                onClick={() => setActiveTab('guidance')}
                className={`flex-1 px-6 py-4 font-semibold transition ${
                  activeTab === 'guidance'
                    ? 'bg-saffron-50 text-saffron-700 border-b-2 border-saffron-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Practical Guidance
              </button>
              <button
                onClick={() => setActiveTab('exercises')}
                className={`flex-1 px-6 py-4 font-semibold transition ${
                  activeTab === 'exercises'
                    ? 'bg-saffron-50 text-saffron-700 border-b-2 border-saffron-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Exercises
              </button>
              <button
                onClick={() => setActiveTab('verses')}
                className={`flex-1 px-6 py-4 font-semibold transition ${
                  activeTab === 'verses'
                    ? 'bg-saffron-50 text-saffron-700 border-b-2 border-saffron-600'
                    : 'text-gray-600 hover:bg-gray-50'
                }`}
              >
                Verses ({result.verses?.length || 0})
              </button>
            </div>
          </div>

          <div className="p-6">
            {activeTab === 'answer' && (
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown>{result.answer}</ReactMarkdown>
              </div>
            )}

            {activeTab === 'analysis' && (
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown>{result.analysis}</ReactMarkdown>
              </div>
            )}

            {activeTab === 'guidance' && (
              <div className="prose prose-lg max-w-none">
                <ReactMarkdown>{result.guidance}</ReactMarkdown>
              </div>
            )}

            {activeTab === 'exercises' && (
              <div className="prose prose-lg max-w-none">
                {result.exercises && result.exercises.trim() ? (
                  <ReactMarkdown>{result.exercises}</ReactMarkdown>
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 italic mb-4">Spiritual exercises are being generated based on the verses referenced above.</p>
                    <p className="text-sm text-gray-400">Please check the "Answer" tab for complete guidance including exercises.</p>
                  </div>
                )}
              </div>
            )}

            {activeTab === 'verses' && (
              <div className="space-y-8">
                {result.verses && result.verses.length > 0 ? (
                  result.verses.map((verse, idx) => (
                    <div key={idx} className={`bg-gradient-to-br from-white to-saffron-50 border border-saffron-200 rounded-xl p-6 shadow-sm hover:shadow-md transition-all duration-200 ${idx > 0 ? 'mt-8' : ''}`}>
                      <div className="flex justify-between items-start mb-5 pb-4 border-b-2 border-saffron-200">
                        <h4 className="text-xl font-bold text-saffron-700">{verse.verse_id}</h4>
                        <span className="text-xs font-semibold text-gray-700 bg-saffron-100 px-3 py-1.5 rounded-full uppercase tracking-wide">
                          Chapter {verse.chapter}, Verse {verse.verse_number}
                        </span>
                      </div>
                      {verse.transliteration && (
                        <div className="mb-5">
                          <p className="text-xs font-semibold text-saffron-700 mb-2 uppercase tracking-wider">Transliteration</p>
                          <p className="text-gray-800 text-lg leading-relaxed bg-white p-4 rounded-lg border-l-4 border-saffron-400 italic whitespace-pre-line font-serif">{verse.transliteration}</p>
                        </div>
                      )}
                      {verse.word_meanings && (
                        <div className="mb-5">
                          <p className="text-xs font-semibold text-saffron-700 mb-2 uppercase tracking-wider">Word Meanings</p>
                          <p className="text-gray-700 text-sm leading-relaxed bg-saffron-50 p-3 rounded-lg">{verse.word_meanings}</p>
                        </div>
                      )}
                      {verse.translation && (
                        <div className="mb-5">
                          <p className="text-xs font-semibold text-saffron-700 mb-2 uppercase tracking-wider">Translation</p>
                          <blockquote className="text-gray-800 text-base leading-relaxed border-l-4 border-saffron-400 pl-4 italic bg-white p-4 rounded-lg shadow-sm">
                            {verse.translation}
                          </blockquote>
                        </div>
                      )}
                      {verse.purport && (
                        <div className="mt-5">
                          <p className="text-xs font-semibold text-saffron-700 mb-2 uppercase tracking-wider">Purport</p>
                          <div className="text-gray-700 leading-relaxed bg-white p-5 rounded-lg border border-gray-200 shadow-sm">
                            <p className="whitespace-pre-wrap">{verse.purport}</p>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div className="text-center py-12">
                    <p className="text-gray-500 text-lg">No verses found</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;

