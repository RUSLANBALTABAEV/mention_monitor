import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiPlus, FiTrash2 } from 'react-icons/fi';

const API_URL = 'http://localhost:8000/api';

export default function MinusWords() {
  const [words, setWords] = useState([]);
  const [newWord, setNewWord] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchWords(); }, []);

  const fetchWords = async () => {
    try {
      const res = await axios.get(`${API_URL}/filters/minus-words`);
      setWords(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const addWord = async () => {
    const text = newWord.trim();
    if (!text) return;
    try {
      await axios.post(`${API_URL}/filters/minus-words`, { text });
      setNewWord('');
      fetchWords();
      toast.success('Минус-слово добавлено');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Ошибка добавления');
    }
  };

  const deleteWord = async (id) => {
    try {
      await axios.delete(`${API_URL}/filters/minus-words/${id}`);
      setWords(w => w.filter(x => x.id !== id));
      toast.success('Минус-слово удалено');
    } catch (e) {
      toast.error('Ошибка удаления');
    }
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">🚫 Минус-слова</h1>
        <p className="text-gray-600 dark:text-gray-400">Упоминания, содержащие эти слова, будут автоматически исключены из результатов.</p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Добавить минус-слово</h2>
        <div className="flex flex-wrap gap-3">
          <div className="flex-1 min-w-[200px]">
            <input
              type="text"
              value={newWord}
              onChange={e => setNewWord(e.target.value)}
              placeholder="Слово для исключения..."
              className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              onKeyDown={e => e.key === 'Enter' && addWord()}
            />
          </div>
          <button
            onClick={addWord}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiPlus className="mr-1" /> Добавить
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Минус-слова ({words.length})</h2>
        {loading ? (
          <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div></div>
        ) : words.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">Минус-слова не добавлены</div>
        ) : (
          <div className="flex flex-wrap gap-2">
            {words.map(w => (
              <div key={w.id} className="inline-flex items-center gap-2 bg-red-100 dark:bg-red-900/30 rounded-full px-3 py-1 text-sm">
                <span className="text-red-700 dark:text-red-300">−{w.text}</span>
                <button onClick={() => deleteWord(w.id)} className="text-red-500 hover:text-red-700">
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