import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, NavLink } from 'react-router-dom';
import { FiSun, FiMoon, FiSearch } from 'react-icons/fi';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Keywords from './components/Keywords';
import Results from './components/Result';
import Sources from './components/Sources';
import MinusWords from './components/MinusWords';
import UserLists from './components/UserLists';
import SettingsPage from './components/SettingsPage';
import Integrations from './components/Integrations';

function App() {
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : window.matchMedia('(prefers-color-scheme: dark)').matches;
  });

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
  }, [darkMode]);

  return (
    <BrowserRouter>
      <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
        {/* Сайдбар */}
        <aside className="w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex flex-col">
          <div className="p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center gap-2">
              <span className="text-2xl">📡</span>
              <span className="text-xl font-semibold text-gray-800 dark:text-white">Mention Monitor</span>
            </div>
          </div>
          <nav className="flex-1 py-6">
            <NavLink
              to="/"
              end
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 border-r-2 border-indigo-500'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              <FiSearch size={18} /> Результаты
            </NavLink>
            <NavLink
              to="/keywords"
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 border-r-2 border-indigo-500'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              🏷️ Ключевые слова
            </NavLink>
            <NavLink
              to="/minus-words"
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 border-r-2 border-indigo-500'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              🚫 Минус-слова
            </NavLink>
            <NavLink
              to="/sources"
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 border-r-2 border-indigo-500'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              🌐 Источники
            </NavLink>
            <NavLink
              to="/users"
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 border-r-2 border-indigo-500'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              👤 Пользователи
            </NavLink>
            <NavLink
              to="/integrations"
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 border-r-2 border-indigo-500'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              🔗 Интеграции CRM
            </NavLink>
            <NavLink
              to="/settings"
              className={({ isActive }) =>
                `flex items-center gap-3 px-6 py-3 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-indigo-50 dark:bg-indigo-900/50 text-indigo-600 dark:text-indigo-400 border-r-2 border-indigo-500'
                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                }`
              }
            >
              ⚙️ Настройки
            </NavLink>
          </nav>
          <div className="p-4 border-t border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white"
            >
              {darkMode ? <FiSun size={18} /> : <FiMoon size={18} />}
              {darkMode ? 'Светлая тема' : 'Тёмная тема'}
            </button>
          </div>
        </aside>

        {/* Основной контент */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-7xl mx-auto px-4 py-8">
            <Routes>
              <Route path="/" element={<Results />} />
              <Route path="/keywords" element={<Keywords />} />
              <Route path="/minus-words" element={<MinusWords />} />
              <Route path="/sources" element={<Sources />} />
              <Route path="/users" element={<UserLists />} />
              <Route path="/integrations" element={<Integrations />} />
              <Route path="/settings" element={<SettingsPage />} />
            </Routes>
          </div>
        </main>

        <ToastContainer position="bottom-right" autoClose={3000} theme={darkMode ? 'dark' : 'light'} />
      </div>
    </BrowserRouter>
  );
}

export default App;