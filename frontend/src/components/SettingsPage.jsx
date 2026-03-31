import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiSave, FiPlay } from 'react-icons/fi';

const API_URL = 'http://localhost:8000/api';

export default function SettingsPage() {
  const [interval, setInterval] = useState(15);
  const [enabled, setEnabled] = useState(true);
  const [saved, setSaved] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = async () => {
      try {
        const res = await axios.get(`${API_URL}/settings/`);
        const settings = res.data;
        const ivSetting = settings.find(s => s.key === 'parser_interval');
        const enSetting = settings.find(s => s.key === 'parser_enabled');
        if (ivSetting) setInterval(parseInt(ivSetting.value));
        if (enSetting) setEnabled(enSetting.value === 'true');
      } catch (e) { console.error(e); }
      finally { setLoading(false); }
    };
    fetch();
  }, []);

  const save = async () => {
    try {
      await axios.put(`${API_URL}/settings/parser_interval`, { value: String(interval) });
      await axios.put(`${API_URL}/settings/parser_enabled`, { value: String(enabled) });
      setSaved(true);
      toast.success('Настройки сохранены');
      setTimeout(() => setSaved(false), 3000);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Ошибка сохранения');
    }
  };

  const runNow = async () => {
    try {
      await axios.post(`${API_URL}/settings/run_now`);
      toast.info('Запуск парсинга инициирован');
    } catch (e) {
      toast.error('Не удалось запустить парсинг');
    }
  };

  if (loading) return <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div></div>;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">⚙️ Настройки</h1>
        <p className="text-gray-600 dark:text-gray-400">Управление режимом работы парсера и расписанием сбора данных.</p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 space-y-6">
        <div>
          <h2 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">Режим работы (24/7)</h2>
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={enabled}
              onChange={e => setEnabled(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Парсинг включён (24/7)</span>
          </label>
        </div>

        <div>
          <h2 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">Интервал обновления</h2>
          <div className="flex items-center gap-3">
            <input
              type="number"
              value={interval}
              onChange={e => setInterval(Math.max(5, Math.min(60, parseInt(e.target.value) || 5)))}
              min={5}
              max={60}
              className="w-24 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
            <span className="text-sm text-gray-500 dark:text-gray-400">минут (от 5 до 60)</span>
          </div>
          <input
            type="range"
            min={5} max={60} step={5}
            value={interval}
            onChange={e => setInterval(parseInt(e.target.value))}
            className="w-64 mt-2 accent-indigo-600"
          />
          <p className="text-sm text-gray-500 dark:text-gray-400 mt-2">
            Парсинг будет запускаться каждые <strong className="text-indigo-600 dark:text-indigo-400">{interval} мин</strong>.
          </p>
        </div>

        <div className="flex gap-3">
          <button
            onClick={save}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiSave className="mr-1" /> Сохранить настройки
          </button>
          <button
            onClick={runNow}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiPlay className="mr-1" /> Запустить парсинг сейчас
          </button>
          {saved && <span className="text-sm text-green-600 dark:text-green-400">✓ Сохранено!</span>}
        </div>

        <div className="pt-4 border-t border-gray-200 dark:border-gray-700">
          <h2 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">Информация о системе</h2>
          <div className="grid grid-cols-2 gap-2 text-sm text-gray-600 dark:text-gray-400">
            <div>Backend</div><div>FastAPI + SQLAlchemy</div>
            <div>БД</div><div>PostgreSQL</div>
            <div>Очереди</div><div>Celery + Redis</div>
            <div>OCR</div><div>Tesseract (rus+eng)</div>
            <div>AI Vision</div><div>Google Vision API / OpenCV</div>
            <div>Frontend</div><div>React + Vite + Tailwind</div>
          </div>
        </div>
      </div>
    </div>
  );
}