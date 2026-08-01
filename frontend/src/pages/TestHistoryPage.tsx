import { useQuery } from '@tanstack/react-query';
import { testsAPI } from '../api/tests';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';

export default function TestHistoryPage() {
  const { t } = useTranslation();

  const { data: tests, isLoading } = useQuery({
    queryKey: ['tests'],
    queryFn: () => testsAPI.getTests(),
  });

  const formatDate = (dateStr: string | null) => {
    if (!dateStr) return 'N/A';
    return new Date(dateStr).toLocaleDateString();
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">{t('tests.history')}</h1>
        <Link to="/tests" className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
          {t('tests.generate')}
        </Link>
      </div>

      {isLoading ? (
        <p>Loading...</p>
      ) : !tests || tests.length === 0 ? (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <p className="text-gray-500">No test history yet</p>
        </div>
      ) : (
        <div className="space-y-4">
          {tests.map((test) => (
            <div key={test.id} className="bg-white p-6 rounded-lg shadow-md">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-lg font-semibold">Test #{test.id}</h3>
                  <p className="text-sm text-gray-600">
                    {formatDate(test.start_date)} - {formatDate(test.end_date)}
                  </p>
                  <p className="text-sm text-gray-500 mt-1">
                    {test.total_questions} questions
                  </p>
                </div>
                <div className="text-right">
                  {test.score !== null ? (
                    <>
                      <div className="text-2xl font-bold text-green-600">
                        {test.score}%
                      </div>
                      <div className="text-sm text-gray-600">
                        {test.correct_answers}/{test.total_questions}
                      </div>
                    </>
                  ) : (
                    <span className="text-gray-500">Not submitted</span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}