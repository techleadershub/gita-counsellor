import { useState, useEffect, useRef } from 'react';
import {
  Search,
  MessageSquare,
  BookOpen,
  Sparkles,
  BrainCircuit,
  CheckCircle2,
  AlertCircle,
  ScrollText,
  Loader2,
  Lightbulb,
  FileText
} from 'lucide-react';

const stepIcons = {
  analyzing: Search,
  questions_generated: MessageSquare,
  researching: BookOpen,
  searching_verse: ScrollText,
  verses_found: Sparkles,
  searching_purports: BookOpen,
  purports_found: Lightbulb,
  synthesizing: BrainCircuit,
  finalizing: FileText,
  completed: CheckCircle2,
  error: AlertCircle
};

const stepLabels = {
  analyzing: 'Analyzing Your Question',
  questions_generated: 'Generating Research Questions',
  researching: 'Searching Bhagavad Gita',
  searching_verse: 'Finding Relevant Verses',
  verses_found: 'Verses Found',
  searching_purports: 'Searching Purports',
  purports_found: 'Purports Found',
  synthesizing: 'Synthesizing Guidance',
  finalizing: 'Finalizing Answer',
  completed: 'Complete',
  error: 'Error'
};

export default function ResearchProgress({ query, context, onComplete, onError }) {
  const [currentStep, setCurrentStep] = useState(null);
  const [message, setMessage] = useState('');
  const [details, setDetails] = useState({});
  const [steps, setSteps] = useState([]);
  const [isComplete, setIsComplete] = useState(false);

  // Use refs to avoid stale closures and dependency issues
  const isCompleteRef = useRef(false);
  const onCompleteRef = useRef(onComplete);
  const onErrorRef = useRef(onError);

  // Update refs when callbacks change
  useEffect(() => {
    onCompleteRef.current = onComplete;
    onErrorRef.current = onError;
  }, [onComplete, onError]);

  useEffect(() => {
    if (!query) return;

    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    const controller = new AbortController();
    let isActive = true;
    isCompleteRef.current = false;

    // Diagnostic logging
    console.log('🔍 ResearchProgress: Starting stream request');
    console.log('🔍 API_URL:', API_URL);
    console.log('🔍 Full URL:', `${API_URL}/api/research/stream`);
    console.log('🔍 Query:', query);
    console.log('🔍 Context:', context);

    // Use fetch with streaming for SSE (since EventSource doesn't support POST)
    fetch(`${API_URL}/api/research/stream`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query, context: context || null }),
      signal: controller.signal
    })
      .then(response => {
        console.log('✅ ResearchProgress: Response received', {
          status: response.status,
          statusText: response.statusText,
          headers: Object.fromEntries(response.headers.entries()),
          hasBody: !!response.body
        });

        if (!response.ok) {
          console.error('❌ ResearchProgress: HTTP error', response.status, response.statusText);
          throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
        }

        if (!response.body) {
          console.error('❌ ResearchProgress: Response body is null');
          throw new Error('Response body is null - streaming not supported');
        }

        console.log('✅ ResearchProgress: Starting to read stream');

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        const MAX_BUFFER_SIZE = 1024 * 1024; // 1MB max buffer size

        function readStream() {
          if (!isActive) return;

          reader.read().then(({ done, value }) => {
            if (done) {
              if (!isCompleteRef.current) {
                onErrorRef.current?.(new Error('Stream ended unexpectedly'));
              }
              return;
            }

            if (!value) {
              // Empty chunk, continue reading
              readStream();
              return;
            }

            // Prevent buffer overflow
            if (buffer.length > MAX_BUFFER_SIZE) {
              console.error('Buffer overflow detected, resetting buffer');
              buffer = '';
              onErrorRef.current?.(new Error('Stream buffer overflow'));
              return;
            }

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // Keep incomplete line in buffer

            for (const line of lines) {
              if (line.trim() === '' || line.startsWith(':')) {
                continue; // Skip empty lines and heartbeats
              }

              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6));
                  console.log('📨 ResearchProgress: Received progress data', data);
                  // Validate required fields
                  if (data && typeof data === 'object' && 'step' in data) {
                    handleProgress(data);
                  } else {
                    console.warn('⚠️ ResearchProgress: Invalid progress data format:', data);
                  }
                } catch (e) {
                  console.error('❌ ResearchProgress: Error parsing SSE data:', e, line);
                  // Continue processing other lines
                }
              } else if (line.startsWith(':')) {
                console.log('💓 ResearchProgress: Heartbeat received');
              }
            }

            readStream();
          }).catch(err => {
            if (err.name !== 'AbortError' && isActive) {
              console.error('❌ ResearchProgress: Stream read error:', {
                name: err.name,
                message: err.message,
                stack: err.stack
              });
              isActive = false;
              isCompleteRef.current = true;
              setIsComplete(true);
              onErrorRef.current?.(err);
            } else if (err.name === 'AbortError') {
              console.log('ℹ️ ResearchProgress: Stream read aborted (expected on cleanup)');
            }
          });
        }

        readStream();
      })
      .catch(err => {
        if (err.name !== 'AbortError' && isActive) {
          console.error('❌ ResearchProgress: Fetch error:', {
            name: err.name,
            message: err.message,
            stack: err.stack,
            API_URL: API_URL,
            fullURL: `${API_URL}/api/research/stream`
          });
          isActive = false;
          isCompleteRef.current = true;
          setIsComplete(true);
          const errorMessage = err.message || 'Failed to connect to server. Please check if the backend is running.';
          onErrorRef.current?.(new Error(errorMessage));
        } else if (err.name === 'AbortError') {
          console.log('ℹ️ ResearchProgress: Request aborted (expected on cleanup)');
        }
      });

    function handleProgress(data) {
      if (!isActive) return;

      // Validate and safely extract data
      const step = data?.step || 'unknown';
      const message = data?.message || '';
      const details = data?.details || {};

      setCurrentStep(step);
      setMessage(message);
      setDetails(details);

      // Add to steps history (limit to prevent memory issues)
      setSteps(prev => {
        const newSteps = [...prev, { step, message, details, timestamp: Date.now() }];
        // Keep only last 50 steps to prevent memory issues
        return newSteps.slice(-50);
      });

      if (step === 'completed') {
        isCompleteRef.current = true;
        setIsComplete(true);
        isActive = false;
        // Validate details before calling onComplete
        if (details && typeof details === 'object') {
          onCompleteRef.current?.(details);
        } else {
          onErrorRef.current?.(new Error('Invalid completion data'));
        }
      } else if (step === 'error') {
        isCompleteRef.current = true;
        setIsComplete(true);
        isActive = false;
        onErrorRef.current?.(new Error(message || 'Unknown error occurred'));
      }
    }

    return () => {
      isActive = false;
      isCompleteRef.current = false;
      controller.abort();
      // Note: reader will be automatically released when AbortController aborts
      // The stream will be cancelled and resources cleaned up
    };
  }, [query, context]);

  if (!query) return null;

  const allSteps = ['analyzing', 'questions_generated', 'researching', 'searching_verse', 'verses_found', 'searching_purports', 'purports_found', 'synthesizing', 'finalizing'];
  const currentStepIndex = allSteps.indexOf(currentStep || 'analyzing');

  return (
    <div className="glass-panel rounded-2xl p-4 sm:p-8 mb-6 sm:mb-8 animate-fade-in shadow-xl shadow-nebula-100/50">
      <h3 className="text-lg sm:text-xl font-bold text-gray-900 mb-4 sm:mb-6 font-serif">Research Progress</h3>

      {/* Current Step */}
      <div className="mb-6 sm:mb-8">
        <div className="flex items-center gap-3 sm:gap-4 mb-3 sm:mb-4">
          <div className="w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-br from-nebula-100 to-nebula-200 flex items-center justify-center text-nebula-700 shadow-sm border border-nebula-200">
            {(() => {
              const Icon = stepIcons[currentStep] || Loader2;
              return <Icon className={`w-5 h-5 sm:w-6 sm:h-6 ${!stepIcons[currentStep] ? 'animate-spin' : ''}`} />;
            })()}
          </div>
          <div className="flex-1">
            <h4 className="font-bold text-base sm:text-lg text-gray-900 leading-tight">
              {stepLabels[currentStep] || 'Processing...'}
            </h4>
            <p className="text-xs sm:text-sm text-gray-600 mt-0.5 sm:mt-1 leading-snug">{message}</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-starlight-200 rounded-full h-2 sm:h-3 mt-3 sm:mt-4 overflow-hidden">
          <div
            className="bg-gradient-to-r from-nebula-500 to-nebula-600 h-full rounded-full transition-all duration-700 ease-out shadow-[0_0_10px_rgba(139,92,246,0.5)]"
            style={{
              width: isComplete
                ? '100%'
                : `${((currentStepIndex + 1) / allSteps.length) * 100}%`
            }}
          />
        </div>
      </div>

      {/* Step Timeline */}
      <div className="space-y-3 sm:space-y-4 max-h-[300px] sm:max-h-[400px] overflow-y-auto pr-1 sm:pr-2 custom-scrollbar">
        {allSteps.map((step, index) => {
          const isActive = step === currentStep;
          const isCompleted = currentStepIndex > index || isComplete;
          const stepData = steps.find(s => s.step === step);
          const StepIcon = stepIcons[step] || Loader2;

          return (
            <div key={step} className={`flex items-start gap-3 sm:gap-4 p-2.5 sm:p-3 rounded-lg transition-colors ${isActive ? 'bg-nebula-50/50 border border-nebula-100' : ''}`}>
              <div
                className={`flex-shrink-0 w-7 h-7 sm:w-8 sm:h-8 rounded-full flex items-center justify-center font-bold text-[10px] sm:text-xs transition-all border ${isCompleted
                  ? 'bg-nebula-600 text-white border-nebula-600 shadow-md shadow-nebula-500/30'
                  : isActive
                    ? 'bg-white text-nebula-600 border-nebula-400 animate-pulse-slow shadow-[0_0_8px_rgba(139,92,246,0.4)]'
                    : 'bg-starlight-100 text-gray-400 border-starlight-200'
                  }`}
              >
                {isCompleted ? <CheckCircle2 className="w-4 h-4 sm:w-5 sm:h-5" /> : index + 1}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className={`text-sm ${isCompleted || isActive ? 'text-nebula-700' : 'text-gray-400'}`}>
                    <StepIcon className="w-3.5 h-3.5 sm:w-4 sm:h-4" />
                  </span>
                  <span
                    className={`font-medium text-sm sm:text-base truncate ${isActive ? 'text-nebula-900' : isCompleted ? 'text-gray-700' : 'text-gray-400'
                      }`}
                  >
                    {stepLabels[step]}
                  </span>
                </div>
                {stepData && (
                  <p className="text-xs text-gray-500 mt-1 pl-6 sm:pl-7 leading-snug">{stepData.message}</p>
                )}
                {/* Details sections shortened for mobile readability if needed, keeping same structure but checking padding */}
                {(step === 'questions_generated' || step === 'verses_found' || step === 'searching_purports' || step === 'purports_found' || (step === 'searching_verse' && details.total)) && details.count !== undefined && (
                  <p className="text-xs text-nebula-600 mt-1 pl-6 sm:pl-7 font-medium">
                    {step === 'questions_generated' && `Generated ${details.count} layout questions`}
                    {step === 'verses_found' && `Found ${details.count} relevant verses`}
                    {step === 'searching_verse' && `Question ${details.current} of ${details.total}`}
                    {step === 'purports_found' && `Found ${details.count} additional verses`}
                  </p>
                )}
                {/* Re-implementing the individual checks to match original logic but compacted */}
                {step === 'questions_generated' && details.count && !stepData && (
                  <p className="text-xs text-nebula-600 mt-1 pl-6 sm:pl-7 font-medium">Generated {details.count} research questions</p>
                )}
                {step === 'verses_found' && details.count && !stepData && (
                  <p className="text-xs text-nebula-600 mt-1 pl-6 sm:pl-7 font-medium">Found {details.count} relevant verses</p>
                )}
                {step === 'searching_verse' && details.current && !stepData && (
                  <p className="text-xs text-nebula-600 mt-1 pl-6 sm:pl-7 font-medium">Question {details.current} of {details.total}</p>
                )}
                {step === 'purports_found' && details.count && !stepData && (
                  <p className="text-xs text-nebula-600 mt-1 pl-6 sm:pl-7 font-medium">Found {details.count} verses from purports</p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Research Questions Preview */}
      {details.questions && details.questions.length > 0 && (
        <div className="mt-6 sm:mt-8 p-4 sm:p-6 bg-white/60 rounded-xl border border-nebula-100 shadow-inner">
          <h4 className="font-bold text-sm sm:text-base text-nebula-900 mb-2 sm:mb-3 font-serif flex items-center gap-2">
            <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5" /> Research Questions Generated
          </h4>
          <ul className="space-y-2 sm:space-y-3">
            {details.questions.slice(0, 3).map((q, idx) => (
              <li key={idx} className="flex items-start gap-2.5 sm:gap-3 text-xs sm:text-sm text-gray-700 bg-white p-2.5 sm:p-3 rounded-lg border border-starlight-100 shadow-sm leading-relaxed">
                <span className="text-nebula-400 mt-0.5">•</span>
                <span>{q}</span>
              </li>
            ))}
            {details.questions.length > 3 && (
              <li className="text-nebula-600 text-xs sm:text-sm font-medium italic pl-2">...and {details.questions.length - 3} more questions</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
