import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  AreaChart,
  Area,
  BarChart,
  Bar,
  Legend,
} from 'recharts';
import type { ProgressData } from '@/types';

interface ProgressChartsProps {
  data: ProgressData;
}

export function ProgressCharts({ data }: ProgressChartsProps) {
  const beliefData = data.belief_history.map((item, index) => ({
    index: index + 1,
    topic: item.topic,
    expected: item.belief.expected_lambda * 100,
    variance: item.belief.variance * 100,
    confidence: item.belief.confidence_interval[1] - item.belief.confidence_interval[0],
  }));

  const accuracyData = data.cumulative_accuracy.map((acc, index) => ({
    question: index + 1,
    accuracy: acc * 100,
  }));

  const levelData = Object.entries(data.level_stats).map(([level, stats]) => ({
    level: `Level ${level}`,
    total: stats.total,
    correct: stats.correct,
    accuracy: stats.total > 0 ? (stats.correct / stats.total) * 100 : 0,
  }));

  return (
    <div className="space-y-6">
      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Belief State Evolution
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={beliefData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="index" 
                stroke="#6b7280"
                tick={{ fontSize: 12 }}
              />
              <YAxis 
                stroke="#6b7280"
                tick={{ fontSize: 12 }}
                domain={[0, 100]}
                label={{ value: 'Expected Mastery (%)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
                formatter={(value: number) => [`${value.toFixed(1)}%`, '']}
              />
              <Area 
                type="monotone" 
                dataKey="expected" 
                stroke="#3b82f6" 
                fill="#3b82f6" 
                fillOpacity={0.2}
                strokeWidth={2}
                name="Expected Mastery"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">
          Cumulative Accuracy
        </h3>
        <div className="h-72">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={accuracyData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
              <XAxis 
                dataKey="question" 
                stroke="#6b7280"
                tick={{ fontSize: 12 }}
                label={{ value: 'Question Number', position: 'insideBottom', offset: -5 }}
              />
              <YAxis 
                stroke="#6b7280"
                tick={{ fontSize: 12 }}
                domain={[0, 100]}
                label={{ value: 'Accuracy (%)', angle: -90, position: 'insideLeft' }}
              />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'white', 
                  border: '1px solid #e5e7eb',
                  borderRadius: '8px',
                  fontSize: '12px'
                }}
                formatter={(value: number) => [`${value.toFixed(1)}%`, 'Accuracy']}
              />
              <Line 
                type="monotone" 
                dataKey="accuracy" 
                stroke="#10b981" 
                strokeWidth={2}
                dot={{ fill: '#10b981', strokeWidth: 2, r: 3 }}
                activeDot={{ r: 5, stroke: '#10b981', strokeWidth: 2 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {levelData.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Performance by Level
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={levelData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="level" 
                  stroke="#6b7280"
                  tick={{ fontSize: 12 }}
                />
                <YAxis 
                  stroke="#6b7280"
                  tick={{ fontSize: 12 }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'white', 
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }}
                />
                <Legend />
                <Bar 
                  dataKey="total" 
                  fill="#e5e7eb" 
                  name="Total Questions"
                  radius={[4, 4, 0, 0]}
                />
                <Bar 
                  dataKey="correct" 
                  fill="#3b82f6" 
                  name="Correct Answers"
                  radius={[4, 4, 0, 0]}
                />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
