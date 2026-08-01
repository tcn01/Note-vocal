import { useState } from 'react';
import type { Vocabulary } from '../types';
import { useTranslation } from 'react-i18next';

interface WordCardProps {
  vocab: Vocabulary;
  onDelete: (id: number) => void;
  onToggleImportant: (id: number) => void;
}

export default function WordCard({ vocab, onDelete, onToggleImportant }: WordCardProps) {
  const { t } = useTranslation();
  const [expanded, setExpanded] = useState(false);

  const audioUrl = vocab.pronunciation_url
    ? `http://localhost:8000${vocab.pronunciation_url}`
    : null;

  return (
    <div className={`border rounded-lg overflow-hidden transition-all ${
      vocab.is_important ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 bg-white'
    }`}>
      {/* Collapsed header — chỉ hiện word + IPA */}
      <div
        className="flex items-center justify-between p-4 cursor-pointer hover:bg-gray-50"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="flex items-center gap-3 flex-1">
          {/* Tick important */}
          <button
            onClick={(e) => { e.stopPropagation(); onToggleImportant(vocab.id); }}
            className={`text-xl ${vocab.is_important ? 'text-yellow-500' : 'text-gray-300 hover:text-gray-400'}`}
            title={vocab.is_important ? 'Bỏ đánh dấu' : 'Đánh dấu quan trọng'}
          >
            {vocab.is_important ? '★' : '☆'}
          </button>

          {/* Word + IPA */}
          <div>
            <span className="text-lg font-semibold text-blue-600">{vocab.word}</span>
            {vocab.ipa && (
              <span className="ml-2 text-sm text-gray-500 font-mono">{vocab.ipa}</span>
            )}
          </div>
        </div>

        <div className="flex items-center gap-2">
          {/* Audio */}
          {audioUrl && (
            <audio src={audioUrl} controls className="h-8 w-32" onClick={(e) => e.stopPropagation()} />
          )}
          {/* Expand icon */}
          <span className={`transform transition-transform ${expanded ? 'rotate-180' : ''}`}>
            ▼
          </span>
        </div>
      </div>

      {/* Expanded content */}
      {expanded && (
        <div className="px-4 pb-4 border-t border-gray-100">
          {/* Definitions */}
          {vocab.definitions.length > 0 && (
            <div className="mt-3 space-y-3">
              <h4 className="text-sm font-medium text-gray-700">{t('vocab.definitions')}</h4>
              {vocab.definitions.map((def, idx) => (
                <div key={idx} className="bg-gray-50 rounded p-3">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-bold bg-blue-100 text-blue-700 px-2 py-0.5 rounded">
                      {def.partOfSpeech}
                    </span>
                  </div>
                  <p className="text-gray-800">{def.meaning}</p>
                  {def.example && (
                    <p className="text-sm text-gray-500 italic mt-1">"{def.example}"</p>
                  )}
                  {def.memory_tip && (
                    <p className="text-sm text-green-600 mt-1">💡 {def.memory_tip}</p>
                  )}
                  {def.notes && (
                    <p className="text-sm text-orange-600 mt-1">📝 {def.notes}</p>
                  )}
                </div>
              ))}
            </div>
          )}

          {/* Memory tip (top-level) */}
          {vocab.memory_tip && (
            <div className="mt-3 text-sm text-green-600">
              <span className="font-medium">💡 {t('vocab.memoryTip')}:</span> {vocab.memory_tip}
            </div>
          )}

          {/* Examples */}
          {vocab.examples.length > 0 && (
            <div className="mt-3">
              <h4 className="text-sm font-medium text-gray-700">{t('vocab.examples')}</h4>
              <ul className="list-disc list-inside text-sm text-gray-600 mt-1">
                {vocab.examples.map((ex, idx) => (
                  <li key={idx}>"{ex}"</li>
                ))}
              </ul>
            </div>
          )}

          {/* Notes */}
          {vocab.notes && (
            <div className="mt-3 text-sm text-orange-600">
              <span className="font-medium">📝 Ghi chú:</span> {vocab.notes}
            </div>
          )}

          {/* Delete button */}
          <div className="mt-3 pt-3 border-t border-gray-100">
            <button
              onClick={() => onDelete(vocab.id)}
              className="text-sm text-red-500 hover:text-red-700 hover:underline"
            >
              Xoá
            </button>
          </div>
        </div>
      )}
    </div>
  );
}