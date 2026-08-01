import { useState, useCallback } from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { vocabularyAPI } from '../api/vocabulary';
import WordCard from '../components/WordCard';
import PendingLookupItem from '../components/PendingLookupItem';
import { useMutation } from '@tanstack/react-query';
import { useTranslation } from 'react-i18next';
import type { Vocabulary } from '../types';

interface PendingLookup {
  id: string;
  word: string;
  language: string;
  status: 'loading' | 'success' | 'error';
  error?: string;
}

function groupByDate(words: Vocabulary[]): Record<string, Vocabulary[]> {
  const groups: Record<string, Vocabulary[]> = {};
  for (const w of words) {
    const key = w.learned_date || 'unknown';
    if (!groups[key]) groups[key] = [];
    groups[key].push(w);
  }
  return groups;
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('vi-VN', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
}

let lookupIdCounter = 0;

export default function VocabularyPage() {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const [word, setWord] = useState('');
  const [language, setLanguage] = useState('en');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [pendingLookups, setPendingLookups] = useState<PendingLookup[]>([]);

  const { data: vocabulary, isLoading } = useQuery({
    queryKey: ['vocabulary', fromDate, toDate],
    queryFn: () => vocabularyAPI.getVocabulary(fromDate || undefined, toDate || undefined),
  });

  // Xoá từ
  const deleteMutation = useMutation({
    mutationFn: (id: number) => vocabularyAPI.deleteWord(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['vocabulary'] }),
  });

  // Đánh dấu quan trọng
  const toggleMutation = useMutation({
    mutationFn: (id: number) => vocabularyAPI.toggleImportant(id),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['vocabulary'] }),
  });

  // Thêm từ vào hàng đợi — không block
  const enqueueLookup = useCallback((word: string, language: string) => {
    const id = `lookup-${++lookupIdCounter}`;
    setPendingLookups((prev) => [...prev, { id, word, language, status: 'loading' }]);

    vocabularyAPI
      .lookupWord({ word, language })
      .then(() => {
        setPendingLookups((prev) =>
          prev.map((p) => (p.id === id ? { ...p, status: 'success' } : p))
        );
        queryClient.invalidateQueries({ queryKey: ['vocabulary'] });
      })
      .catch((err: any) => {
        const detail =
          err.response?.status === 409
            ? `"${word}" đã tồn tại`
            : err.response?.data?.detail || 'Lỗi tra cứu';
        setPendingLookups((prev) =>
          prev.map((p) => (p.id === id ? { ...p, status: 'error', error: detail } : p))
        );
      });
  }, [queryClient]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!word.trim()) return;
    enqueueLookup(word.trim(), language);
    setWord('');
  };

  const dismissLookup = (id: string) => {
    setPendingLookups((prev) => prev.filter((p) => p.id !== id));
  };

  const groups = vocabulary ? groupByDate(vocabulary) : {};

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold mb-6">{t('vocab.title')}</h1>

      {/* Add Word Form — không bao giờ bị block */}
      <div className="bg-white p-6 rounded-lg shadow-md mb-6">
        <h2 className="text-xl font-semibold mb-4">{t('vocab.addWord')}</h2>

        <form onSubmit={handleSubmit} className="flex gap-4 items-end flex-wrap">
          <div className="flex-1 min-w-[200px]">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('vocab.word')}
            </label>
            <input
              type="text"
              value={word}
              onChange={(e) => setWord(e.target.value)}
              required
              placeholder="Nhập từ cần tra..."
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="w-32">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('vocab.language')}
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="en">English</option>
              <option value="vi">Tiếng Việt</option>
              <option value="zh">中文</option>
              <option value="ja">日本語</option>
              <option value="ko">한국어</option>
            </select>
          </div>

          <button
            type="submit"
            className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 min-w-[100px]"
          >
            {t('vocab.lookup')}
          </button>
        </form>
      </div>

      {/* Pending lookups queue */}
      {pendingLookups.length > 0 && (
        <div className="mb-6 space-y-2">
          {pendingLookups.map((item) => (
            <PendingLookupItem key={item.id} item={item} onDismiss={dismissLookup} />
          ))}
        </div>
      )}

      {/* Date Filter */}
      <div className="bg-white p-4 rounded-lg shadow-md mb-6">
        <h3 className="text-lg font-semibold mb-2">{t('vocab.filter')}</h3>
        <div className="flex gap-4 items-end flex-wrap">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('vocab.from')}</label>
            <input
              type="date"
              value={fromDate}
              onChange={(e) => setFromDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">{t('vocab.to')}</label>
            <input
              type="date"
              value={toDate}
              onChange={(e) => setToDate(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <button
            onClick={() => queryClient.invalidateQueries({ queryKey: ['vocabulary'] })}
            className="bg-gray-600 text-white px-4 py-2 rounded-md hover:bg-gray-700"
          >
            {t('vocab.apply')}
          </button>
          {(fromDate || toDate) && (
            <button
              onClick={() => { setFromDate(''); setToDate(''); }}
              className="text-gray-500 hover:text-gray-700 text-sm"
            >
              Xoá lọc
            </button>
          )}
        </div>
      </div>

      {/* Vocabulary List — Grouped by Date */}
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h2 className="text-xl font-semibold mb-4">{t('vocab.myWords')}</h2>

        {isLoading ? (
          <div className="flex justify-center py-8">
            <svg className="animate-spin h-8 w-8 text-blue-600" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
          </div>
        ) : !vocabulary || vocabulary.length === 0 ? (
          <p className="text-gray-500 text-center py-8">
            Chưa có từ vựng nào. Hãy thêm từ mới để bắt đầu học!
          </p>
        ) : (
          <div className="space-y-6">
            {Object.entries(groups).map(([date, words]) => (
              <div key={date}>
                <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-wider mb-3">
                  {formatDate(date)}
                  <span className="ml-2 text-xs font-normal text-gray-400">
                    ({words.length} từ)
                  </span>
                </h3>
                <div className="space-y-2">
                  {words.map((vocab) => (
                    <WordCard
                      key={vocab.id}
                      vocab={vocab}
                      onDelete={(id) => { if (confirm('Xoá từ này?')) deleteMutation.mutate(id); }}
                      onToggleImportant={(id) => toggleMutation.mutate(id)}
                    />
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}