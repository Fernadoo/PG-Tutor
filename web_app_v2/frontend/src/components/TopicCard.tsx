import { BookOpen, Signal, BarChart2, Clock } from 'lucide-react';
import type { Topic, BeliefState } from '@/types';

interface TopicCardProps {
  topic: Topic;
  belief?: BeliefState;
  lessonContent?: string | null;
}

export default function TopicCard({ topic, belief, lessonContent }: TopicCardProps) {
  const getMasteryColor = (mastery: number) => {
    if (mastery >= 0.8) return 'bg-green-100 text-green-800';
    if (mastery >= 0.6) return 'bg-blue-100 text-blue-800';
    if (mastery >= 0.4) return 'bg-yellow-100 text-yellow-800';
    return 'bg-red-100 text-red-800';
  };

  const mastery = belief?.expected_lambda || 0;

  return (
    <div className="card space-y-4">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
              <BookOpen className="w-5 h-5 text-primary-600" />
            </div>
            <div>
              <h3 className="text-xl font-bold text-gray-900">{topic.name}</h3>
              <div className="flex items-center gap-3 text-sm text-gray-600 mt-1">
                <span className="flex items-center gap-1">
                  <Signal className="w-4 h-4" />
                  Level {topic.level}
                </span>
                <span className="w-px h-3 bg-gray-300" />
                <span>Difficulty: {topic.difficulty.toFixed(2)}</span>
              </div>
            </div>
          </div>
        </div>
        
        {belief && (
          <div className={`
            px-3 py-1.5 rounded-full text-sm font-medium
            ${getMasteryColor(mastery)}
          `}>
            {(mastery * 100).toFixed(0)}% Mastery
          </div>
        )}
      </div>

      <div className="prose prose-blue max-w-none">
        <div className="bg-gray-50 rounded-lg p-4 text-gray-700 leading-relaxed whitespace-pre-wrap">
          {lessonContent || topic.content}
        </div>
      </div>

      {topic.prerequisites.length > 0 && (
        <div className="pt-4 border-t border-gray-200">
          <div className="flex items-center gap-2 text-sm text-gray-600 mb-2">
            <Clock className="w-4 h-4" />
            Prerequisites:
          </div>
          <div className="flex flex-wrap gap-2">
            {topic.prerequisites.map((prereq) => (
              <span 
                key={prereq}
                className="px-2 py-1 bg-gray-100 text-gray-700 text-sm rounded-md"
              >
                {prereq}
              </span>
            ))}
          </div>
        </div>
      )}

      {belief && (
        <div className="grid grid-cols-3 gap-3 pt-4 border-t border-gray-200">
          <div className="p-3 bg-primary-50 rounded-lg">
            <div className="flex items-center gap-1.5 text-primary-700 text-sm mb-1">
              <BarChart2 className="w-4 h-4" />
              Expected
            </div>
            <div className="text-lg font-semibold text-primary-900">
              {(belief.expected_lambda * 100).toFixed(1)}%
            </div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-gray-600 text-sm mb-1">α Parameter</div>
            <div className="text-lg font-semibold text-gray-900">
              {belief.alpha.toFixed(2)}
            </div>
          </div>
          <div className="p-3 bg-gray-50 rounded-lg">
            <div className="text-gray-600 text-sm mb-1">β Parameter</div>
            <div className="text-lg font-semibold text-gray-900">
              {belief.beta.toFixed(2)}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
