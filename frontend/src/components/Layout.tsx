import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';

const nav = [
  { path: '/', label: 'Dashboard', icon: '◈' },
  { path: '/machines', label: 'Machines', icon: '⊞' },
  { path: '/commands', label: 'Commands', icon: '⌘' },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const { pathname } = useLocation();
  const { logout, isAdmin } = useAuth();

  return (
    <div className="flex h-screen bg-gray-950 text-gray-300">
      <aside className="w-56 bg-gray-900 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <h1 className="text-lg font-semibold text-white">RTK Dashboard</h1>
        </div>
        <nav className="flex-1 p-2 space-y-1">
          {nav.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm ${
                pathname === item.path
                  ? 'bg-sky-600 text-white'
                  : 'hover:bg-gray-800 text-gray-400'
              }`}
            >
              <span>{item.icon}</span>
              {item.label}
            </Link>
          ))}
          {isAdmin && (
            <Link
              to="/admin"
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm ${
                pathname === '/admin' || pathname.startsWith('/admin/')
                  ? 'bg-sky-600 text-white'
                  : 'hover:bg-gray-800 text-gray-400'
              }`}
            >
              <span>⚙</span>
              Admin
            </Link>
          )}
        </nav>
        <div className="p-3 border-t border-gray-800">
          <button
            onClick={logout}
            className="text-sm text-gray-500 hover:text-gray-300 w-full text-left"
          >
            Logout
          </button>
        </div>
      </aside>
      <main className="flex-1 overflow-auto p-6">{children}</main>
    </div>
  );
}
