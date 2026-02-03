import { useQuery } from '@tanstack/react-query';
import { History, Calendar, CheckCircle, XCircle, Brain } from 'lucide-react';
import { useStore } from '@/store';
import { sessionApi } from '@/api/client';
import { formatDistanceToNow } from '@/utils/date';

export default function HistoryPage() {
  const { session } = useStore();
  const sessionId = session?.session_id;

  const { data: progress, isLoading, error } = useQuery({
    queryKey: ['history', sessionId],
    queryFn: () => sessionId ? sessionApi.getProgress(sessionId) : null,
    enabled: !!sessionId,
  });

  if (!session) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500">No active session</div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-pulse text-gray-500">Loading history...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-red-600">Failed to load history</div>
      </div>
    );
  }

  const beliefHistory = progress?.belief_history || [];
  const topicHistory = progress?.topic_history || [];

  const allHistory = [
    ...beliefHistory.map((item) => ({
      type: 'answer' as const,
      topic: item.topic,
      correct: item.correct,
      timestamp: item.timestamp,
      belief: item.belief,
    })),
    ...topicHistory.map((item) => ({
      type: 'topic' as const,
      topic: item.topic,
      level: item.level,
      correct: item.correct,
      timestamp: item.timestamp,
    })),
  ].sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <History className="w-6 h-6 text-primary-600" />
        <h1 className="text-2xl font-bold text-gray-900">Session History</h1>
      </div>

      <div className="card">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
            <p className="text-sm text-gray-600 mt-1">
              {allHistory.length} total interactions
            </p>
          </div>
        </div>

        {allHistory.length === 0 ? (
          <div className="text-center py-12">
            <Brain className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">No history yet. Start learning to see your progress!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {allHistory.slice(0, 50).map((item, index) => (
              <div 
                key={index} 
                className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className={`
                  w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0
                  ${item.correct ? 'bg-green-100' : 'bg-red-100'}
                `}>
                  {item.correct ? (
                    <CheckCircle className="w-5 h-5 text-green-600" />
                  ) : (
                    <XCircle className="w-5 h-5 text-red-600" />
                  )}
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-4">
                    <h4 className="font-medium text-gray-900 truncate">
                      {item.topic}
                    </h4>
                    <div className="flex items-center gap-1 text-sm text-gray-500 flex-shrink-0">
                      <Calendar className="w-4 h-4" />
                      {formatDistanceToNow(item.timestamp)}
                    </div>
                  </div>

                  <div className="flex items-center gap-4 mt-2">
                    <span className={`
                      text-sm font-medium px-2 py-1 rounded-full
                      ${item.correct 
                        ? 'bg-green-100 text-green-700' 
                        : 'bg-red-100 text-red-700'}
                    `}>
                      {item.correct ? 'Correct' : 'Incorrect'}
                    </span>
                    
                    {'level' in item && (
                      <span className="text-sm text-gray-600">
                        Level {item.level}
                      </span>
                    )}
                    
                    {'belief' in item && item.belief && (
                      <span className="text-sm text-gray-600">
                        Mastery: {(item.belief.expected_lambda * 100).toFixed(1)}%
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {allHistory.length > 50 && (
          <div className="text-center mt-6 pt-6 border-t border-gray-200">
            <p className="text-sm text-gray-500">
              Showing 50 of {allHistory.length} interactions
            </p>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Session Stats</h3>
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-gray-600">Session ID</span>
              <span className="font-mono text-sm text-gray-900">
                {session.session_id.slice(0, 8)}...
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Mode</span>
              <span className="font-medium text-gray-900 capitalize">
                {session.mode}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Created</span>
              <span className="text-gray-900">
                {formatDistanceToNow(session.created_at)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600">Last Updated</span>
              <span className="text-gray-900">
                {formatDistanceToNow(session.updated_at)}
              </span>
            </div>
          </div>
        </div>

        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Topics Covered</h3>
          <div className="text-3xl font-bold text-primary-600 mb-1">
            {new Set(allHistory.map(h => h.topic)).size}
          </div>
          <p className="text-gray-600">unique topics</p>
        </div>
      </div>
    </div>
  );
}
