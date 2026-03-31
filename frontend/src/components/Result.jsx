import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { format } from 'date-fns';
import { ru as ruLocale } from 'date-fns/locale'; // ✅
import { FiTrash2, FiDownload, FiSearch } from 'react-icons/fi';
import { toast } from 'react-toastify';

const API_URL = 'http://localhost:8000/api';

export default function Results() {
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    source_type: '',
    content_type: '',
    keyword: '',
    country: '',
    city: '',
    date_from: '',
    date_to: '',
  });
  const [exporting, setExporting] = useState(false);

  const fetchResults = useCallback(async () => {
    setLoading(true);
    try {
      const params = Object.fromEntries(
        Object.entries(filters).filter(([, v]) => v !== '')
      );
      const res = await axios.get(`${API_URL}/results/`, { params });
      setResults(res.data);
    } catch (e) {
      console.error(e);
      toast.error('Ошибка загрузки результатов');
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => { fetchResults(); }, [fetchResults]);

  const handleExport = async (fmt) => {
    setExporting(true);
    try {
      const params = {
        format: fmt,
        ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v !== '')),
      };
      const res = await axios.get(`${API_URL}/results/export`, {
        params,
        responseType: 'blob',
      });
      const ext = fmt === 'excel' ? 'xlsx' : fmt;
      const url = window.URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `mentions.${ext}`;
      a.click();
      window.URL.revokeObjectURL(url);
      toast.success(`Экспорт в ${fmt.toUpperCase()} выполнен`);
    } catch (e) {
      toast.error('Ошибка экспорта');
    } finally {
      setExporting(false);
    }
  };

  const deleteResult = async (id) => {
    if (!confirm('Удалить упоминание?')) return;
    try {
      await axios.delete(`${API_URL}/results/${id}`);
      setResults(r => r.filter(x => x.id !== id));
      toast.success('Упоминание удалено');
    } catch (e) {
      toast.error('Ошибка удаления');
    }
  };

  const resetFilters = () => {
    setFilters({
      source_type: '', content_type: '', keyword: '',
      country: '', city: '', date_from: '', date_to: '',
    });
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">Результаты мониторинга</h1>
        <p className="text-gray-600 dark:text-gray-400">Найдено: <strong>{results.length}</strong> упоминаний</p>
      </div>

      {/* Фильтры */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-4">
          <select
            value={filters.source_type}
            onChange={e => setFilters({ ...filters, source_type: e.target.value })}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="">Все источники</option>
            <option value="vk">VK</option>
            <option value="tenchat">TenChat</option>
            <option value="max">Max</option>
            <option value="site">Сайт</option>
          </select>
          <select
            value={filters.content_type}
            onChange={e => setFilters({ ...filters, content_type: e.target.value })}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          >
            <option value="">Все типы</option>
            <option value="text">Текст</option>
            <option value="image">Изображение</option>
            <option value="story">Story</option>
          </select>
          <input
            type="text"
            placeholder="Ключевое слово"
            value={filters.keyword}
            onChange={e => setFilters({ ...filters, keyword: e.target.value })}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <input
            type="text"
            placeholder="Страна"
            value={filters.country}
            onChange={e => setFilters({ ...filters, country: e.target.value })}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <input
            type="text"
            placeholder="Город"
            value={filters.city}
            onChange={e => setFilters({ ...filters, city: e.target.value })}
            className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
          />
          <div className="flex items-center space-x-2">
            <input
              type="datetime-local"
              value={filters.date_from}
              onChange={e => setFilters({ ...filters, date_from: e.target.value })}
              className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
            <span>—</span>
            <input
              type="datetime-local"
              value={filters.date_to}
              onChange={e => setFilters({ ...filters, date_to: e.target.value })}
              className="block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end space-x-2">
          <button
            onClick={fetchResults}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiSearch className="mr-1" /> Применить
          </button>
          <button
            onClick={resetFilters}
            className="inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md shadow-sm text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600 dark:hover:bg-gray-700"
          >
            Сбросить
          </button>
        </div>

        {/* Экспорт */}
        <div className="mt-4 flex gap-2 border-t pt-4 border-gray-200 dark:border-gray-700">
          <span className="text-sm text-gray-600 dark:text-gray-400">Экспорт:</span>
          <button
            onClick={() => handleExport('csv')}
            disabled={exporting}
            className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 dark:bg-gray-800 dark:text-gray-300 dark:border-gray-600"
          >
            <FiDownload className="mr-1" /> CSV
          </button>
          <button
            onClick={() => handleExport('excel')}
            disabled={exporting}
            className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiDownload className="mr-1" /> Excel
          </button>
          <button
            onClick={() => handleExport('json')}
            disabled={exporting}
            className="inline-flex items-center px-3 py-1 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiDownload className="mr-1" /> JSON
          </button>
        </div>
      </div>

      {/* Результаты */}
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-500"></div>
        </div>
      ) : results.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-12 text-center">
          <div className="mx-auto h-24 w-24 text-gray-400">
            <svg className="h-full w-full" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Упоминания не найдены</h3>
          <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Попробуйте изменить фильтры или добавьте ключевые слова.</p>
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 shadow overflow-hidden sm:rounded-lg">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead className="bg-gray-50 dark:bg-gray-900">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">#</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Текст</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Источник</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Тип</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Автор</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Гео</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Ключевое слово</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider">Дата</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wider"></th>
                </tr>
              </thead>
              <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                {results.map(r => (
                  <tr key={r.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{r.id}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 dark:text-white max-w-xs truncate">{r.text || r.ocr_text}</td>
                    <td className="px-6 py-4 text-sm">
                      <a href={r.source_url} target="_blank" rel="noopener noreferrer" className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400">
                        {r.source_url?.substring(0, 40)}…
                      </a>
                      <div className="mt-1 text-xs text-gray-500">{r.source_type}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{r.content_type}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{r.author || '—'}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {r.geo_city ? `${r.geo_city}, ${r.geo_country || ''}` : '—'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-indigo-600 dark:text-indigo-400">{r.keyword}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {format(new Date(r.date), 'dd.MM.yyyy HH:mm', { locale: ru })}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button onClick={() => deleteResult(r.id)} className="text-red-600 hover:text-red-900 dark:text-red-400">
                        <FiTrash2 />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}