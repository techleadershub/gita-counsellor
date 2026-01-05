import { useState, useEffect, useRef } from 'react';

const stepIcons = {
  analyzing: '🔍',
  questions_generated: '💭',
  researching: '📚',
  searching_verse: '🔎',
  verses_found: '✨',
  synthesizing: '🧘',
  finalizing: '📝',
  completed: '✅',
  error: '❌'
};

const stepLabels = {
  analyzing: 'Analyzing Your Question',
  questions_generated: 'Generating Research Questions',
  researching: 'Searching Bhagavad Gita',
  searching_verse: 'Finding Relevant Verses',
  verses_found: 'Verses Found',
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

  const allSteps = ['analyzing', 'questions_generated', 'researching', 'searching_verse', 'verses_found', 'synthesizing', 'finalizing'];
  const currentStepIndex = allSteps.indexOf(currentStep || 'analyzing');

  return (
    <div className="bg-white rounded-xl shadow-lg p-6 mb-6">
      <h3 className="text-xl font-bold text-gray-800 mb-4">Research Progress</h3>
      
      {/* Current Step */}
      <div className="mb-6">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-3xl">{stepIcons[currentStep] || '⏳'}</span>
          <div className="flex-1">
            <h4 className="font-semibold text-gray-800">
              {stepLabels[currentStep] || 'Processing...'}
            </h4>
            <p className="text-sm text-gray-600">{message}</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-gray-200 rounded-full h-2 mt-3">
          <div
            className="bg-saffron-600 h-2 rounded-full transition-all duration-500"
            style={{
              width: isComplete
                ? '100%'
                : `${((currentStepIndex + 1) / allSteps.length) * 100}%`
            }}
          />
        </div>
      </div>

      {/* Step Timeline */}
      <div className="space-y-3">
        {allSteps.map((step, index) => {
          const isActive = step === currentStep;
          const isCompleted = currentStepIndex > index || isComplete;
          const stepData = steps.find(s => s.step === step);

          return (
            <div key={step} className="flex items-start gap-3">
              <div
                className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-semibold text-sm transition-all ${
                  isCompleted
                    ? 'bg-saffron-600 text-white'
                    : isActive
                    ? 'bg-saffron-400 text-white animate-pulse'
                    : 'bg-gray-200 text-gray-500'
                }`}
              >
                {isCompleted ? '✓' : index + 1}
              </div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-lg">{stepIcons[step]}</span>
                  <span
                    className={`font-medium ${
                      isActive ? 'text-saffron-700' : isCompleted ? 'text-gray-700' : 'text-gray-400'
                    }`}
                  >
                    {stepLabels[step]}
                  </span>
                </div>
                {stepData && (
                  <p className="text-xs text-gray-500 mt-1 ml-7">{stepData.message}</p>
                )}
                {step === 'questions_generated' && details.count && (
                  <p className="text-xs text-saffron-600 mt-1 ml-7">
                    Generated {details.count} research questions
                  </p>
                )}
                {step === 'verses_found' && details.count && (
                  <p className="text-xs text-saffron-600 mt-1 ml-7">
                    Found {details.count} relevant verses
                  </p>
                )}
                {step === 'searching_verse' && details.current && details.total && (
                  <p className="text-xs text-saffron-600 mt-1 ml-7">
                    Question {details.current} of {details.total}
                  </p>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {/* Research Questions Preview */}
      {details.questions && details.questions.length > 0 && (
        <div className="mt-6 p-4 bg-saffron-50 rounded-lg border border-saffron-200">
          <h4 className="font-semibold text-saffron-800 mb-2">Research Questions:</h4>
          <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
            {details.questions.slice(0, 3).map((q, idx) => (
              <li key={idx}>{q}</li>
            ))}
            {details.questions.length > 3 && (
              <li className="text-saffron-600">...and {details.questions.length - 3} more</li>
            )}
          </ul>
        </div>
      )}
    </div>
  );
}
