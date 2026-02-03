import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, ArrowRight, RotateCcw, Sparkles, Loader2 } from 'lucide-react';
import { useStore } from '@/store';
import { sessionApi } from '@/api/client';
import TopicCard from '@/components/TopicCard';
import AnswerInput from '@/components/AnswerInput';

export default function Lesson() {
  const { 
    session, 
    setSession, 
    lastAnswer, 
    setLastAnswer, 
    clearLastAnswer,
    mode 
  } = useStore();
  
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lessonContent, setLessonContent] = useState<string | null>(null);
  const [isLoadingLesson, setIsLoadingLesson] = useState(false);

  // Fetch lesson content when session or topic changes
  useEffect(() => {
    if (!session) return;
    
    const fetchLesson = async () => {
      // For LLM mode, fetch generated content
      if (mode === 'llm') {
        setIsLoadingLesson(true);
        try {
          const lesson = await sessionApi.getLesson(session.session_id);
          setLessonContent(lesson.lesson_content);
        } catch (err) {
          console.error('Failed to fetch lesson:', err);
          // Fall back to static content
          setLessonContent(session.current_topic.content);
        } finally {
          setIsLoadingLesson(false);
        }
      } else {
        // For simple mode, use static content
        setLessonContent(session.current_topic.content);
      }
    };

    fetchLesson();
  }, [session?.current_topic?.id, mode, session?.session_id]);

  if (!session) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">No active session</div>
      </div>
    );
  }

  const handleSubmitAnswer = async (answer: string) => {
    if (!session || !answer.trim()) return;
    
    setIsSubmitting(true);
    setError(null);

    try {
      const response = await sessionApi.submitAnswer(session.session_id, {
        answer,
        use_llm: mode === 'llm',
      });

      setLastAnswer(response);

      if (response.next_topic) {
        setSession({
          ...session,
          current_topic: response.next_topic,
          belief: response.updated_belief,
          total_answered: response.total_answered,
          correct_count: response.correct_count,
          accuracy: response.accuracy,
        });
        // Lesson content will be fetched by useEffect when topic changes
      } else {
        setSession({
          ...session,
          belief: response.updated_belief,
          total_answered: response.total_answered,
          correct_count: response.correct_count,
          accuracy: response.accuracy,
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit answer');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleNext = () => {
    clearLastAnswer();
    // Reset lesson content for next question
    setLessonContent(null);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-gray-900">Current Lesson</h1>
        <div className="flex items-center gap-4 text-sm text-gray-600">
          <span>Level {session.current_topic.level}</span>
          <span className="w-px h-4 bg-gray-300" />
          <span>Difficulty: {session.current_topic.difficulty.toFixed(2)}</span>
          {mode === 'llm' && (
            <>
              <span className="w-px h-4 bg-gray-300" />
              <span className="flex items-center gap-1 text-primary-600">
                <Sparkles className="w-4 h-4" />
                AI Tutor
              </span>
            </>
          )}
        </div>
      </div>

      {isLoadingLesson ? (
        <div className="card flex items-center justify-center py-12">
          <div className="flex items-center gap-3 text-gray-600">
            <Loader2 className="w-6 h-6 animate-spin" />
            <span>Generating personalized lesson...</span>
          </div>
        </div>
      ) : (
        <TopicCard 
          topic={session.current_topic} 
          belief={session.belief}
          lessonContent={lessonContent}
        />
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700 text-sm">
          {error}
        </div>
      )}

      {!lastAnswer ? (
        <AnswerInput 
          onSubmit={handleSubmitAnswer} 
          isLoading={isSubmitting}
          mode={mode}
        />
      ) : (
        <div className="card space-y-6">
          <div className={`flex items-center gap-3 p-4 rounded-lg ${
            lastAnswer.correct 
              ? 'bg-green-50 border border-green-200' 
              : 'bg-red-50 border border-red-200'
          }`}>
            {lastAnswer.correct ? (
              <CheckCircle className="w-6 h-6 text-green-600" />
            ) : (
              <XCircle className="w-6 h-6 text-red-600" />
            )}
            <div>
              <div className={`font-medium ${
                lastAnswer.correct ? 'text-green-800' : 'text-red-800'
              }`}>
                {lastAnswer.correct ? 'Correct!' : 'Incorrect'}
              </div>
              <div className={`text-sm ${
                lastAnswer.correct ? 'text-green-700' : 'text-red-700'
              }`}>
                {lastAnswer.feedback}
              </div>
            </div>
          </div>

          {mode === 'llm' && lastAnswer.llm_evaluation && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-2 text-blue-800 font-medium mb-2">
                <Sparkles className="w-4 h-4" />
                LLM Evaluation
              </div>
              <pre className="text-sm text-blue-700 overflow-auto max-h-40">
                {JSON.stringify(lastAnswer.llm_evaluation, null, 2)}
              </pre>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Updated Belief</div>
              <div className="text-lg font-medium text-gray-900 mt-1">
                α={lastAnswer.updated_belief.alpha.toFixed(2)}, 
                β={lastAnswer.updated_belief.beta.toFixed(2)}
              </div>
              <div className="text-sm text-gray-500 mt-1">
                Expected: {(lastAnswer.updated_belief.expected_lambda * 100).toFixed(1)}%
              </div>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Progress</div>
              <div className="text-lg font-medium text-gray-900 mt-1">
                {lastAnswer.correct_count}/{lastAnswer.total_answered} correct
              </div>
              <div className="text-sm text-gray-500 mt-1">
                {(lastAnswer.accuracy * 100).toFixed(1)}% accuracy
              </div>
            </div>
          </div>

          {lastAnswer.next_topic && (
            <div className="p-4 bg-primary-50 border border-primary-200 rounded-lg">
              <div className="text-primary-800 font-medium">
                Next Topic: {lastAnswer.next_topic.name}
              </div>
              <div className="text-sm text-primary-600 mt-1">
                Level {lastAnswer.next_topic.level} • Difficulty {lastAnswer.next_topic.difficulty.toFixed(2)}
              </div>
            </div>
          )}

          <button
            onClick={handleNext}
            className="w-full btn-primary flex items-center justify-center gap-2"
          >
            Continue
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      )}

      {lastAnswer && !lastAnswer.next_topic && (
        <div className="card text-center py-8">
          <div className="w-16 h-16 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <RotateCcw className="w-8 h-8 text-yellow-600" />
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">
            Session Target Reached!
          </h3>
          <p className="text-gray-600 mb-4">
            You've completed {session.total_answered} questions. Great job!
          </p>
          <button
            onClick={handleNext}
            className="btn-secondary"
          >
            Continue Practicing
          </button>
        </div>
      )}
    </div>
  );
}
