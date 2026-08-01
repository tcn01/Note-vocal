import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTranslation } from 'react-i18next';

export default function Navbar() {
  const { t, i18n } = useTranslation();
  const { user, logout, isAuthenticated } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  const isActive = (path: string) => location.pathname === path;

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const changeLanguage = (lng: string) => {
    i18n.changeLanguage(lng);
  };

  if (!isAuthenticated) return null;

  return (
    <nav className="bg-blue-600 text-white shadow-lg">
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center h-16">
          <div className="flex items-center space-x-4">
            <Link to="/vocabulary" className="font-bold text-xl">
              VisionNest
            </Link>
            <div className="hidden md:flex space-x-4">
              <Link
                to="/vocabulary"
                className={`px-3 py-2 rounded ${
                  isActive('/vocabulary') ? 'bg-blue-700' : 'hover:bg-blue-500'
                }`}
              >
                {t('nav.vocabulary')}
              </Link>
              <Link
                to="/grammar"
                className={`px-3 py-2 rounded ${
                  isActive('/grammar') ? 'bg-blue-700' : 'hover:bg-blue-500'
                }`}
              >
                {t('nav.grammar')}
              </Link>
              <Link
                to="/tests"
                className={`px-3 py-2 rounded ${
                  isActive('/tests') ? 'bg-blue-700' : 'hover:bg-blue-500'
                }`}
              >
                {t('nav.tests')}
              </Link>
              <Link
                to="/tests/history"
                className={`px-3 py-2 rounded ${
                  isActive('/tests/history') ? 'bg-blue-700' : 'hover:bg-blue-500'
                }`}
              >
                {t('tests.history')}
              </Link>
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <select
              value={i18n.language}
              onChange={(e) => changeLanguage(e.target.value)}
              className="bg-blue-700 text-white px-2 py-1 rounded text-sm"
            >
              <option value="vi">VI</option>
              <option value="en">EN</option>
            </select>

            <span className="text-sm hidden sm:inline">{user?.name}</span>

            <button
              onClick={handleLogout}
              className="bg-blue-700 hover:bg-blue-800 px-3 py-1 rounded text-sm"
            >
              {t('nav.logout')}
            </button>
          </div>
        </div>

        {/* Mobile menu */}
        <div className="md:hidden pb-4 flex flex-col space-y-2">
          <Link
            to="/vocabulary"
            className={`px-3 py-2 rounded ${
              isActive('/vocabulary') ? 'bg-blue-700' : 'hover:bg-blue-500'
            }`}
          >
            {t('nav.vocabulary')}
          </Link>
          <Link
            to="/grammar"
            className={`px-3 py-2 rounded ${
              isActive('/grammar') ? 'bg-blue-700' : 'hover:bg-blue-500'
            }`}
          >
            {t('nav.grammar')}
          </Link>
          <Link
            to="/tests"
            className={`px-3 py-2 rounded ${
              isActive('/tests') ? 'bg-blue-700' : 'hover:bg-blue-500'
            }`}
          >
            {t('nav.tests')}
          </Link>
          <Link
            to="/tests/history"
            className={`px-3 py-2 rounded ${
              isActive('/tests/history') ? 'bg-blue-700' : 'hover:bg-blue-500'
            }`}
          >
            {t('tests.history')}
          </Link>
        </div>
      </div>
    </nav>
  );
}