import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiPlus, FiTrash2 } from 'react-icons/fi';

const API_URL = 'http://localhost:8000/api';

export default function Keywords() {
  const [keywords, setKeywords] = useState([]);
  const [newKeyword, setNewKeyword] = useState('');
  const [operator, setOperator] = useState('OR');
  const [exactMatch, setExactMatch] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchKeywords(); }, []);

  const fetchKeywords = async () => {
    try {
      const res = await axios.get(`${API_URL}/keywords`);
      setKeywords(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const addKeyword = async () => {
    const text = newKeyword.trim();
    if (!text) return;
    try {
      await axios.post(`${API_URL}/keywords`, { text, operator, exact_match: exactMatch });
      setNewKeyword('');
      fetchKeywords();
      toast.success('Ключевое слово добавлено');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Ошибка добавления');
    }
  };

  const deleteKeyword = async (id) => {
    try {
      await axios.delete(`${API_URL}/keywords/${id}`);
      setKeywords(kw => kw.filter(x => x.id !== id));
      toast.success('Ключевое слово удалено');
    } catch (e) {
      toast.error('Ошибка удаления');
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">🏷️ Ключевые слова</h1>
        <p className="text-gray-600 dark:text-gray-400">Слова для поиска упоминаний. Поддерживается логика AND / OR и точное совпадение.</p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Добавить ключевое слово</h2>
        <div className="flex flex-wrap gap-3 items-end">
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              value={newKeyword}
              onChange={e => setNewKeyword(e.target.value)}
              placeholder="Введите ключевое слово..."
              className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              onKeyDown={e => e.key === 'Enter' && addKeyword()}
            />
          </div>
          <select
            value={operator}
            onChange={e => setOperator(e.target.value)}
            className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
          >
            <option value="OR">OR — любое из слов</option>
            <option value="AND">AND — все слова</option>
          </select>
          <label className="inline-flex items-center">
            <input
              type="checkbox"
              checked={exactMatch}
              onChange={e => setExactMatch(e.target.checked)}
              className="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500"
            />
            <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Точное совпадение</span>
          </label>
          <button
            onClick={addKeyword}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiPlus className="mr-1" /> Добавить
          </button>
        </div>
        <p className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          <strong>OR</strong>: найдёт упоминания с любым из слов. &nbsp;
          <strong>AND</strong>: найдёт только если присутствуют все слова. &nbsp;
          <strong>Точное совпадение</strong>: только целые слова (не части).
        </p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Список ключевых слов ({keywords.length})</h2>
        {loading ? (
          <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div></div>
        ) : keywords.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">Ключевые слова не добавлены</div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {keywords.map(kw => (
              <div key={kw.id} className="inline-flex items-center gap-2 bg-gray-100 dark:bg-gray-700 rounded-full px-3 py-1 text-sm">
                <span className="text-gray-800 dark:text-gray-200">{kw.text}</span>
                <span className="text-xs text-gray-500 dark:text-gray-400">{kw.operator}{kw.exact_match ? ' • точно' : ''}</span>
                <button onClick={() => deleteKeyword(kw.id)} className="text-red-500 hover:text-red-700">
                  <FiTrash2 size={14} />
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}