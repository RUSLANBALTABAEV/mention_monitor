import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiPlus, FiTrash2, FiZap } from 'react-icons/fi'; // ✅ FiZap или FiActivity

const API_URL = 'http://localhost:8000/api';
const CRM_TYPES = ['amoCRM', 'Bitrix24'];
const CONTENT_TYPES = ['text', 'image', 'story'];

export default function Integrations() {
  const [integrations, setIntegrations] = useState([]);
  const [form, setForm] = useState({
    name: 'amoCRM',
    webhook_url: '',
    is_active: true,
    send_on_types: ['text', 'story', 'image'],
  });
  const [testing, setTesting] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchIntegrations(); }, []);

  const fetchIntegrations = async () => {
    try {
      const res = await axios.get(`${API_URL}/integrations/`);
      setIntegrations(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const addIntegration = async () => {
    if (!form.webhook_url.trim()) {
      toast.warn('Введите URL вебхука');
      return;
    }
    try {
      await axios.post(`${API_URL}/integrations/`, form);
      setForm({ name: 'amoCRM', webhook_url: '', is_active: true, send_on_types: ['text', 'story', 'image'] });
      fetchIntegrations();
      toast.success('Интеграция добавлена');
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Ошибка добавления');
    }
  };

  const deleteIntegration = async (id) => {
    if (!confirm('Удалить интеграцию?')) return;
    try {
      await axios.delete(`${API_URL}/integrations/${id}`);
      setIntegrations(i => i.filter(x => x.id !== id));
      toast.success('Интеграция удалена');
    } catch (e) {
      toast.error('Ошибка удаления');
    }
  };

  const testIntegration = async (id) => {
    setTesting(id);
    try {
      const res = await axios.post(`${API_URL}/integrations/${id}/test`);
      if (res.data.ok) {
        toast.success(`Тест успешен! Статус: ${res.data.status}`);
      } else {
        toast.error(`Ошибка: ${res.data.error || res.data.response}`);
      }
    } catch (e) {
      toast.error('Ошибка соединения с CRM');
    } finally {
      setTesting(null);
    }
  };

  const toggleType = (type) => {
    setForm(f => ({
      ...f,
      send_on_types: f.send_on_types.includes(type)
        ? f.send_on_types.filter(t => t !== type)
        : [...f.send_on_types, type],
    }));
  };

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">🔗 Интеграции с CRM</h1>
        <p className="text-gray-600 dark:text-gray-400">Автоматическая отправка новых упоминаний в amoCRM или Bitrix24 через вебхук.</p>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Добавить интеграцию</h2>
        <div className="space-y-4">
          <div className="flex flex-wrap gap-3">
            <select
              value={form.name}
              onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
              className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              {CRM_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
            </select>
            <div className="flex-1 min-w-[300px]">
              <input
                type="url"
                value={form.webhook_url}
                onChange={e => setForm(f => ({ ...f, webhook_url: e.target.value }))}
                placeholder="https://..."
                className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
              />
            </div>
            <label className="inline-flex items-center">
              <input
                type="checkbox"
                checked={form.is_active}
                onChange={e => setForm(f => ({ ...f, is_active: e.target.checked }))}
                className="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500"
              />
              <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Активна</span>
            </label>
          </div>

          <div>
            <div className="text-sm text-gray-600 dark:text-gray-400 mb-2">Отправлять при типах упоминаний:</div>
            <div className="flex gap-4">
              {CONTENT_TYPES.map(t => (
                <label key={t} className="inline-flex items-center">
                  <input
                    type="checkbox"
                    checked={form.send_on_types.includes(t)}
                    onChange={() => toggleType(t)}
                    className="rounded border-gray-300 text-indigo-600 shadow-sm focus:ring-indigo-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{t}</span>
                </label>
              ))}
            </div>
          </div>

          <button
            onClick={addIntegration}
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <FiPlus className="mr-1" /> Добавить
          </button>
        </div>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Настроенные интеграции ({integrations.length})</h2>
        {loading ? (
          <div className="flex justify-center py-8"><div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div></div>
        ) : integrations.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">CRM-интеграции не настроены</div>
        ) : (
          <div className="space-y-3">
            {integrations.map(crm => (
              <div key={crm.id} className="flex justify-between items-start p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-medium text-gray-900 dark:text-white">{crm.name}</span>
                    <span className={`text-xs px-2 py-0.5 rounded ${crm.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'}`}>
                      {crm.is_active ? 'активна' : 'отключена'}
                    </span>
                  </div>
                  <div className="text-sm text-gray-500 dark:text-gray-400 break-all">{crm.webhook_url}</div>
                  <div className="text-xs text-gray-400 mt-1">Типы: {crm.send_on_types?.join(', ') || 'все'}</div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={() => testIntegration(crm.id)}
                    disabled={testing === crm.id}
                    className="text-indigo-600 hover:text-indigo-800 dark:text-indigo-400 dark:hover:text-indigo-300"
                    title="Тест"
                  >
                    <FiZap />
                  </button>
                  <button
                    onClick={() => deleteIntegration(crm.id)}
                    className="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300"
                    title="Удалить"
                  >
                    <FiTrash2 />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mt-6">
        <h2 className="text-lg font-medium mb-4 text-gray-900 dark:text-white">Как настроить вебхук</h2>
        <div className="text-sm text-gray-600 dark:text-gray-400 space-y-2">
          <p><strong className="text-indigo-600 dark:text-indigo-400">amoCRM:</strong> Зайдите в Настройки → Интеграции → Вебхуки → скопируйте URL вебхука.</p>
          <p><strong className="text-indigo-600 dark:text-indigo-400">Bitrix24:</strong> Перейдите в Приложения → Вебхуки → Входящий вебхук → добавьте и скопируйте URL.</p>
          <p>При каждом новом упоминании система автоматически POST-запросом отправит данные на указанный URL.</p>
        </div>
      </div>
    </div>
  );
}