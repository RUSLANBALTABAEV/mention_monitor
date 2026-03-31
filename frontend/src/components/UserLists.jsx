import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast } from 'react-toastify';
import { FiPlus, FiTrash2 } from 'react-icons/fi';

const API_URL = 'http://localhost:8000/api';
const SOURCE_TYPES = ['vk', 'tenchat', 'max', 'site'];

function UserListSection({ title, endpoint, icon, description }) {
  const [users, setUsers] = useState([]);
  const [username, setUsername] = useState('');
  const [sourceType, setSourceType] = useState('vk');
  const [loading, setLoading] = useState(true);

  useEffect(() => { fetchUsers(); }, []);

  const fetchUsers = async () => {
    try {
      const res = await axios.get(`${API_URL}/filters/${endpoint}`);
      setUsers(res.data);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  const addUser = async () => {
    const u = username.trim();
    if (!u) return;
    try {
      await axios.post(`${API_URL}/filters/${endpoint}`, { username: u, source_type: sourceType });
      setUsername('');
      fetchUsers();
      toast.success(`Пользователь добавлен в ${title}`);
    } catch (e) {
      toast.error(e.response?.data?.detail || 'Ошибка добавления');
    }
  };

  const deleteUser = async (id) => {
    try {
      await axios.delete(`${API_URL}/filters/${endpoint}/${id}`);
      setUsers(u => u.filter(x => x.id !== id));
      toast.success(`Пользователь удалён из ${title}`);
    } catch (e) {
      toast.error('Ошибка удаления');
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow p-6 mb-6">
      <h2 className="text-lg font-medium mb-2 text-gray-900 dark:text-white">{icon} {title} ({users.length})</h2>
      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">{description}</p>

      <div className="flex flex-wrap gap-3 mb-4">
        <div className="flex-1 min-w-[200px]">
          <input
            type="text"
            value={username}
            onChange={e => setUsername(e.target.value)}
            placeholder="Имя пользователя / ID"
            className="w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
            onKeyDown={e => e.key === 'Enter' && addUser()}
          />
        </div>
        <select
          value={sourceType}
          onChange={e => setSourceType(e.target.value)}
          className="rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 shadow-sm focus:border-indigo-500 focus:ring-indigo-500"
        >
          {SOURCE_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
        </select>
        <button
          onClick={addUser}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
        >
          <FiPlus className="mr-1" /> Добавить
        </button>
      </div>

      {loading ? (
        <div className="flex justify-center py-4"><div className="animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-500"></div></div>
      ) : users.length === 0 ? (
        <p className="text-center text-gray-500 dark:text-gray-400">Список пуст</p>
      ) : (
        <div className="space-y-2">
          {users.map(u => (
            <div key={u.id} className="flex justify-between items-center p-2 bg-gray-50 dark:bg-gray-700 rounded">
              <span className="text-gray-800 dark:text-gray-200">
                {u.username} <span className="text-xs text-gray-500">({u.source_type})</span>
              </span>
              <button onClick={() => deleteUser(u.id)} className="text-red-500 hover:text-red-700">
                <FiTrash2 />
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function UserLists() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white">👤 Управление пользователями</h1>
        <p className="text-gray-600 dark:text-gray-400">Чёрный список исключает пользователей из результатов. Белый список — пропускает только указанных.</p>
      </div>

      <UserListSection
        title="Чёрный список пользователей"
        endpoint="user-blacklist"
        icon="🚫"
        description="Упоминания от этих пользователей будут полностью исключены из мониторинга."
      />

      <UserListSection
        title="Белый список пользователей"
        endpoint="user-whitelist"
        icon="✅"
        description="Если список не пуст — показываются только упоминания от этих пользователей (опционально)."
      />
    </div>
  );
}