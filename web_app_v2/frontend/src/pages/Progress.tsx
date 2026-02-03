import { useQuery } from '@tanstack/react-query';
import { useStore } from '@/store';
import { sessionApi } from '@/api/client';
import { ProgressCharts } from '@/components/ProgressCharts';
import { BarChart3, TrendingUp, Target, Award } from 'lucide-react';

export default function Progress() {
  const { session } = useStore();
  const sessionId = session?.session_id;

  const { data: progress, isLoading, error } = useQuery({
    queryKey: ['progress', sessionId],
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
        <div className="animate-pulse text-gray-500">Loading progress...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-red-600">Failed to load progress data</div>
      </div>
    );
  }

  const levelStats = progress?.level_stats || {};
  const totalCorrect = Object.values(levelStats).reduce((sum, stat) => sum + stat.correct, 0);
  const totalQuestions = Object.values(levelStats).reduce((sum, stat) => sum + stat.total, 0);
  const overallAccuracy = totalQuestions > 0 ? (totalCorrect / totalQuestions) * 100 : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <BarChart3 className="w-6 h-6 text-primary-600" />
          <h1 className="text-2xl font-bold text-gray-900">Learning Progress</h1>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <Target className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{session.total_answered}</div>
              <div className="text-sm text-gray-600">Questions Answered</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
              <Award className="w-5 h-5 text-green-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">{session.correct_count}</div>
              <div className="text-sm text-gray-600">Correct Answers</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
              <TrendingUp className="w-5 h-5 text-blue-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {(session.accuracy * 100).toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Current Accuracy</div>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
              <BarChart3 className="w-5 h-5 text-purple-600" />
            </div>
            <div>
              <div className="text-2xl font-bold text-gray-900">
                {overallAccuracy.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Overall Accuracy</div>
            </div>
          </div>
        </div>
      </div>

      {progress && <ProgressCharts data={progress} />}

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance by Level</h3>
        <div className="space-y-3">
          {Object.entries(levelStats).length === 0 ? (
            <p className="text-gray-500">No data available yet. Start answering questions!</p>
          ) : (
            Object.entries(levelStats)
              .sort(([a], [b]) => parseInt(a) - parseInt(b))
              .map(([level, stats]) => {
                const accuracy = stats.total > 0 ? (stats.correct / stats.total) * 100 : 0;
                return (
                  <div key={level} className="flex items-center gap-4">
                    <div className="w-20 text-sm font-medium text-gray-700">
                      Level {level}
                    </div>
                    <div className="flex-1">
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-primary-500 rounded-full transition-all duration-500"
                          style={{ width: `${accuracy}%` }}
                        />
                      </div>
                    </div>
                    <div className="w-24 text-sm text-gray-600 text-right">
                      {stats.correct}/{stats.total} ({accuracy.toFixed(0)}%)
                    </div>
                  </div>
                );
              })
          )}
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Current Belief State</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Alpha (α)</div>
            <div className="text-2xl font-bold text-gray-900">
              {session.belief.alpha.toFixed(3)}
            </div>
            <div className="text-xs text-gray-500 mt-1">Success parameter</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Beta (β)</div>
            <div className="text-2xl font-bold text-gray-900">
              {session.belief.beta.toFixed(3)}
            </div>
            <div className="text-xs text-gray-500 mt-1">Failure parameter</div>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <div className="text-sm text-gray-600 mb-1">Expected Mastery</div>
            <div className="text-2xl font-bold text-primary-600">
              {(session.belief.expected_lambda * 100).toFixed(1)}%
            </div>
            <div className="text-xs text-gray-500 mt-1">
              CI: [{session.belief.confidence_interval[0].toFixed(2)}, {session.belief.confidence_interval[1].toFixed(2)}]
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
