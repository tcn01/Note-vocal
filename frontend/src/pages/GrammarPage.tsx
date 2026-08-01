import { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { grammarAPI } from '../api/grammar';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';

export default function GrammarPage() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [showLesson, setShowLesson] = useState(false);
  const [currentLesson, setCurrentLesson] = useState<any>(null);

  const { data: todayPlan, isLoading: loadingPlan } = useQuery({
    queryKey: ['grammarToday'],
    queryFn: () => grammarAPI.getTodayPlan(),
  });

  const generateMutation = useMutation({
    mutationFn: (topicId: number) => grammarAPI.generateLesson({ topic_id: topicId }),
    onSuccess: (data) => {
      setCurrentLesson(data);
      setShowLesson(true);
      queryClient.invalidateQueries({ queryKey: ['grammarToday'] });
    },
  });

  const updateMutation = useMutation({
    mutationFn: ({ lessonId, data }: { lessonId: number; data: any }) =>
      grammarAPI.updateLesson(lessonId, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['grammarToday'] });
    },
  });

  const handleGenerateLesson = (topicId: number) => {
    generateMutation.mutate(topicId);
  };

  const handleComplete = (lessonId: number) => {
    updateMutation.mutate({
      lessonId,
      data: { is_completed: true },
    });
    setShowLesson(false);
    setCurrentLesson(null);
  };

  if (loadingPlan) {
    return <div className="container mx-auto px-4 py-8">Loading...</div>;
  }

  // No grammar level set
  if (!user?.grammar_level) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">{t('grammar.setLevel')}</h1>
        <div className="grid md:grid-cols-2 gap-4">
          {['A1', 'A2', 'B1', 'B2'].map((level) => (
            <Link
              key={level}
              to={`/profile?set-level=${level}`}
              className="bg-blue-600 text-white p-6 rounded-lg hover:bg-blue-700 text-center"
            >
              <h3 className="text-xl font-bold">{level}</h3>
              <p className="text-sm mt-2">
                {level === 'A1' && t('grammar.levelA1')}
                {level === 'A2' && t('grammar.levelA2')}
                {level === 'B1' && t('grammar.levelB1')}
                {level === 'B2' && t('grammar.levelB2')}
              </p>
            </Link>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{t('grammar.title')}</h1>
        <Link to="/grammar/curriculum" className="text-blue-600 hover:underline">
          {t('grammar.curriculum')}
        </Link>
      </div>

      {showLesson && currentLesson ? (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-bold mb-4">{currentLesson.topic}</h2>
          <div className="prose max-w-none mb-6">
            <p className="whitespace-pre-line">{currentLesson.explanation}</p>
          </div>

          {currentLesson.examples && currentLesson.examples.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Examples:</h3>
              <ul className="list-disc list-inside space-y-2">
                {currentLesson.examples.map((ex: any, idx: number) => (
                  <li key={idx}>
                    <strong>{ex.sentence}</strong>
                    <br />
                    <span className="text-gray-600">{ex.translation}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {currentLesson.exercises && currentLesson.exercises.length > 0 && (
            <div className="mb-6">
              <h3 className="text-lg font-semibold mb-2">Exercises:</h3>
              <div className="space-y-4">
                {currentLesson.exercises.map((ex: any, idx: number) => (
                  <div key={idx} className="border p-4 rounded">
                    <p className="font-medium mb-2">{ex.question}</p>
                    {ex.options && (
                      <div className="space-y-1">
                        {ex.options.map((opt: string, optIdx: number) => (
                          <label key={optIdx} className="flex items-center gap-2">
                            <input type="radio" name={`exercise-${idx}`} className="rounded" />
                            {opt}
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => handleComplete(currentLesson.id)}
            disabled={updateMutation.isPending}
            className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
          >
            {t('grammar.complete')}
          </button>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Review Section */}
          {todayPlan?.review && (
            <div className="bg-yellow-50 border border-yellow-200 p-6 rounded-lg">
              <h2 className="text-xl font-bold mb-2 text-yellow-800">{t('grammar.review')}</h2>
              <p className="mb-4">{todayPlan.review.topic}</p>
              <button
                onClick={() => handleComplete(todayPlan.review!.id)}
                className="bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700"
              >
                {t('grammar.reviewDone')}
              </button>
            </div>
          )}

          {/* New Lesson Section */}
          {todayPlan?.new && (
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h2 className="text-xl font-bold mb-2">{t('grammar.new')}</h2>
              <p className="text-gray-600 mb-4">{todayPlan.new.description}</p>
              <button
                onClick={() => handleGenerateLesson(todayPlan.new!.id)}
                disabled={generateMutation.isPending}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                {generateMutation.isPending ? t('vocab.loading') : t('grammar.learnNow')}
              </button>
            </div>
          )}

          {/* Daily Limit Reached */}
          {!todayPlan?.review && !todayPlan?.new && (
            <div className="bg-green-50 border border-green-200 p-6 rounded-lg">
              <p className="text-green-800 mb-4">{todayPlan?.message || t('grammar.limitReached')}</p>
              <Link
                to="/grammar/next"
                className="text-blue-600 hover:underline"
              >
                {t('grammar.learnMore')}
              </Link>
            </div>
          )}
        </div>
      )}
    </div>
  );
}