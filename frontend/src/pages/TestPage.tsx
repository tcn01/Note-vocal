import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useMutation } from '@tanstack/react-query';
import { testsAPI } from '../api/tests';
import { useTranslation } from 'react-i18next';

export default function TestPage() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [error, setError] = useState('');
  const [generatedTest, setGeneratedTest] = useState<any>(null);
  const [answers, setAnswers] = useState<Record<string, string>>({});

  const generateMutation = useMutation({
    mutationFn: (data: { start_date: string; end_date: string }) =>
      testsAPI.generateTest(data),
    onSuccess: (data) => {
      setGeneratedTest(data);
      setError('');
    },
    onError: (err: any) => {
      setError(err.response?.data?.detail || 'Error generating test');
    },
  });

  const submitMutation = useMutation({
    mutationFn: ({ testId, answers }: { testId: number; answers: Record<string, string> }) =>
      testsAPI.submitTest(testId, { answers }),
  });

  const handleGenerate = () => {
    if (!startDate || !endDate) {
      setError('Please select date range');
      return;
    }
    generateMutation.mutate({ start_date: startDate, end_date: endDate });
  };

  const handleAnswer = (questionId: number, answer: string) => {
    setAnswers((prev) => ({ ...prev, [questionId.toString()]: answer }));
  };

  const handleSubmit = () => {
    if (!generatedTest) return;
    submitMutation.mutate(
      { testId: generatedTest.id, answers },
      {
        onSuccess: (result) => {
          alert(`Score: ${result.score}% (${result.correct_answers}/${result.total_questions})`);
          setGeneratedTest(null);
          setAnswers({});
          navigate('/tests/history');
        },
      }
    );
  };

  if (generatedTest) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-6">Test</h1>
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">
            {generatedTest.total_questions} Questions
          </h2>

          <div className="space-y-6">
            {generatedTest.questions.map((q: any) => (
              <div key={q.id} className="border p-4 rounded-lg">
                <p className="font-medium mb-3">
                  {q.id}. {q.question}
                </p>

                {q.type === 'multiple_choice' && q.options && (
                  <div className="space-y-2">
                    {q.options.map((opt: string, idx: number) => (
                      <label key={idx} className="flex items-center gap-2">
                        <input
                          type="radio"
                          name={`q-${q.id}`}
                          value={opt}
                          checked={answers[q.id.toString()] === opt}
                          onChange={(e) => handleAnswer(q.id, e.target.value)}
                        />
                        {opt}
                      </label>
                    ))}
                  </div>
                )}

                {q.type === 'fill_in_blank' && (
                  <input
                    type="text"
                    value={answers[q.id.toString()] || ''}
                    onChange={(e) => handleAnswer(q.id, e.target.value)}
                    className="border p-2 rounded w-full"
                    placeholder="Type your answer"
                  />
                )}

                {q.type === 'listening' && q.word_audio && (
                  <div className="mb-3">
                    <audio
                      src={`http://localhost:8000/static/audio/${q.word_audio}.mp3`}
                      controls
                      className="h-8"
                    />
                  </div>
                )}

                {q.type === 'listening' && q.options && (
                  <div className="space-y-2">
                    {q.options.map((opt: string, idx: number) => (
                      <label key={idx} className="flex items-center gap-2">
                        <input
                          type="radio"
                          name={`q-${q.id}`}
                          value={opt}
                          checked={answers[q.id.toString()] === opt}
                          onChange={(e) => handleAnswer(q.id, e.target.value)}
                        />
                        {opt}
                      </label>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="mt-6 flex gap-4">
            <button
              onClick={handleSubmit}
              disabled={submitMutation.isPending}
              className="bg-green-600 text-white px-6 py-2 rounded-md hover:bg-green-700 disabled:opacity-50"
            >
              {t('tests.submit')}
            </button>
            <button
              onClick={() => setGeneratedTest(null)}
              className="bg-gray-600 text-white px-4 py-2 rounded-md"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{t('tests.title')}</h1>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">{t('tests.selectDate')}</h2>
        <div className="flex gap-4 items-end flex-wrap">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('tests.from')}
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('tests.to')}
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <button
            onClick={handleGenerate}
            disabled={generateMutation.isPending}
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {generateMutation.isPending ? t('tests.loading') : t('tests.create')}
          </button>
        </div>
      </div>
    </div>
  );
}