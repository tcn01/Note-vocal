interface PendingLookup {
  id: string;
  word: string;
  language: string;
  status: 'loading' | 'success' | 'error';
  error?: string;
}

interface Props {
  item: PendingLookup;
  onDismiss: (id: string) => void;
}

export default function PendingLookupItem({ item, onDismiss }: Props) {
  const langLabel: Record<string, string> = {
    en: 'EN', vi: 'VI', zh: '中文', ja: '日本語', ko: '한국어',
  };

  if (item.status === 'success') return null;

  return (
    <div className={`flex items-center justify-between px-4 py-3 rounded-lg border ${
      item.status === 'loading'
        ? 'bg-blue-50 border-blue-200'
        : 'bg-red-50 border-red-200'
    }`}>
      <div className="flex items-center gap-3">
        <span className="text-xs font-bold bg-gray-200 text-gray-700 px-2 py-0.5 rounded">
          {langLabel[item.language] || item.language}
        </span>
        <span className="font-medium">{item.word}</span>

        {item.status === 'loading' && (
          <span className="flex items-center gap-2 text-sm text-blue-600">
            <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
            </svg>
            Đang tra cứu...
          </span>
        )}

        {item.status === 'error' && (
          <span className="text-sm text-red-600">{item.error}</span>
        )}
      </div>

      {item.status === 'error' && (
        <button
          onClick={() => onDismiss(item.id)}
          className="text-gray-400 hover:text-gray-600 text-lg leading-none"
        >
          ×
        </button>
      )}
    </div>
  );
}