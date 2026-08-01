import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { authAPI } from '../api/auth';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

export default function ProfilePage() {
  const { t } = useTranslation();
  const { user, logout } = useAuth();
  const [grammarLevel, setGrammarLevel] = useState(user?.grammar_level || '');
  const [language, setLanguage] = useState(user?.preferred_language || 'vi');

  const setLevelMutation = useMutation({
    mutationFn: (level: string) => authAPI.setGrammarLevel(level),
    onSuccess: () => {
      window.location.reload();
    },
  });

  const handleSetLevel = () => {
    if (grammarLevel) {
      setLevelMutation.mutate(grammarLevel);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-6">{t('profile.title')}</h1>

      <div className="bg-white p-6 rounded-lg shadow-md max-w-2xl">
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('profile.name')}
            </label>
            <input
              type="text"
              value={user?.name || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('profile.email')}
            </label>
            <input
              type="email"
              value={user?.email || ''}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-md bg-gray-100"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('profile.grammarLevel')}
            </label>
            <select
              value={grammarLevel}
              onChange={(e) => setGrammarLevel(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="">Select level</option>
              <option value="A1">A1 - Beginner</option>
              <option value="A2">A2 - Elementary</option>
              <option value="B1">B1 - Intermediate</option>
              <option value="B2">B2 - Upper Intermediate</option>
            </select>
            <button
              onClick={handleSetLevel}
              disabled={setLevelMutation.isPending || !grammarLevel}
              className="mt-2 bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {t('profile.save')}
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              {t('profile.language')}
            </label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
              <option value="zh">中文</option>
              <option value="ja">日本語</option>
              <option value="ko">한국어</option>
            </select>
          </div>

          <div className="pt-4 border-t">
            <button
              onClick={logout}
              className="bg-red-600 text-white px-6 py-2 rounded-md hover:bg-red-700"
            >
              {t('nav.logout')}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}