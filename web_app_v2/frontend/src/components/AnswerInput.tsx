import { useState } from 'react';
import { Send, Check, X, Loader2 } from 'lucide-react';

interface AnswerInputProps {
  onSubmit: (answer: string) => void;
  isLoading: boolean;
  mode: 'llm' | 'simple';
}

export default function AnswerInput({ onSubmit, isLoading, mode }: AnswerInputProps) {
  const [textAnswer, setTextAnswer] = useState('');

  const handleTextSubmit = () => {
    if (textAnswer.trim()) {
      onSubmit(textAnswer.trim());
      setTextAnswer('');
    }
  };

  const handleBinarySubmit = (answer: boolean) => {
    onSubmit(answer ? 'true' : 'false');
  };

  if (mode === 'simple') {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Is this statement correct?
        </h3>
        <p className="text-sm text-gray-600 mb-6">
          Choose your answer below. The system will adapt based on your response.
        </p>
        
        <div className="flex gap-4">
          <button
            onClick={() => handleBinarySubmit(true)}
            disabled={isLoading}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <Check className="w-5 h-5" />
                True
              </>
            )}
          </button>
          
          <button
            onClick={() => handleBinarySubmit(false)}
            disabled={isLoading}
            className="flex-1 flex items-center justify-center gap-2 px-6 py-4 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <X className="w-5 h-5" />
                False
              </>
            )}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Your Answer
      </h3>
      <p className="text-sm text-gray-600 mb-4">
        Provide your answer below. The LLM will evaluate it and provide detailed feedback.
      </p>
      
      <div className="space-y-4">
        <textarea
          value={textAnswer}
          onChange={(e) => setTextAnswer(e.target.value)}
          placeholder="Type your answer here..."
          rows={4}
          className="input-field resize-none"
          disabled={isLoading}
        />
        
        <div className="flex justify-end">
          <button
            onClick={handleTextSubmit}
            disabled={isLoading || !textAnswer.trim()}
            className="btn-primary flex items-center gap-2"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                Evaluating...
              </>
            ) : (
              <>
                <Send className="w-4 h-4" />
                Submit Answer
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
