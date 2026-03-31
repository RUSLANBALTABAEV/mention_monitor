import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiPlus, FiTrash2 } from 'react-icons/fi';

const API_URL = 'http://localhost:8000/api';

export default function Sources() {
  const [sources, setSources] = useState([]);
  const [newUrl, setNewUrl] = useState('');
  const [newType, setNewType] = useState('site');
  const [isWhitelist, setIsWhitelist] = useState(true);
  const [priority, setPriority] = useState(5);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchSources(); }, []);

  const fetchSources = async () => {
    try {
      const res = await axios.get(`${API_URL}/sources`);
      setSources(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const addSource = async () => {
    const url = newUrl.trim();
    if (!url) return;
    try {
      await axios.post(`${API_URL}/sources`, { url, type: newType, is_whitelist: isWhitelist, priority });
      setNewUrl('');
      fetchSources();
      toast.success('Источник добавлен');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Ошибка добавления');
    }
  };

  const deleteSource = async (id) => {
    try {
      await axios.delete(`${API_URL}/sources/${id}`);
      setSources(s => s.filter(x => x.id !== id));
      toast.success('Источник удалён');
    } catch (e) {
      toast.error('Ошибка удаления');
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">🌐 Источники</h1>
        <p className="text-gray-600 dark:text-gray-400">Управление белым и чёрным списками источников.</p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Добавить источник</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[250px]">
            <input
              type="text"
              value={newUrl}
              onChange={e => setNewUrl(e.target.value)}
              placeholder="URL источника"
              className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            />
          </div>
          <select
            value={newType}
            onChange={e => setNewType(e.target.value)}
            className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="site">Сайт</option>
            <option value="vk">VK</option>
            <option value="tenchat">TenChat</option>
            <option value="max">Max</option>
          </select>
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={isWhitelist}
              onChange={e => setIsWhitelist(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Белый список</span>
          </label>
          <input
            type="number"
            value={priority}
            onChange={e => setPriority(parseInt(e.target.value))}
            min="1"
            max="10"
            className="w-20 rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          />
          <button
            onClick={addSource}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiPlus className="mr-1" /> Добавить
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Список источников ({sources.length})</h2>
        {loading ? (
          <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div></div>
        ) : sources.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">Источники не добавлены</div>
        ) : (
          <div className="space-y-2">
            {sources.map(s => (
              <div key={s.id} className="flex justify-between items-center p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <div className="font-medium text-gray-900 dark:text-white">{s.url}</div>
                  <div className="text-sm text-gray-500 dark:text-gray-400">
                    {s.type} · {s.is_whitelist ? 'белый список' : 'чёрный список'} · приоритет {s.priority}
                  </div>
                </div>
                <button
                  onClick={() => deleteSource(s.id)}
                  className="text-red-500 hover:text-red-700"
                >
                  <FiTrash2 />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}