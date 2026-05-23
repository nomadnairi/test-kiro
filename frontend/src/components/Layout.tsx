import { Outlet, Link, useLocation } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import {
  LayoutDashboard,
  Search,
  Network,
  Shield,
  Database,
  MessageSquare,
  LogOut,
  Activity,
} from 'lucide-react';

export default function Layout() {
  const location = useLocation();
  const { user, logout } = useAuthStore();

  const navigation = [
    { name: 'Dashboard', href: '/', icon: LayoutDashboard },
    { name: 'Scans', href: '/scans', icon: Search },
    { name: 'Graph', href: '/graph', icon: Network },
    { name: 'IOCs', href: '/iocs', icon: Shield },
    { name: 'Entities', href: '/entities', icon: Database },
    { name: 'AI Chat', href: '/chat', icon: MessageSquare },
  ];

  return (
    <div className="min-h-screen bg-cyber-bg cyber-grid">
      {/* Sidebar */}
      <aside className="fixed inset-y-0 left-0 w-64 bg-cyber-surface border-r border-cyber-border">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="flex items-center gap-3 px-6 py-6 border-b border-cyber-border">
            <Activity className="w-8 h-8 text-cyber-primary animate-pulse-slow" />
            <div>
              <h1 className="text-xl font-bold glow-text">CyberIntel</h1>
              <p className="text-xs text-gray-500">AI Platform</p>
            </div>
          </div>

          {/* Navigation */}
          <nav className="flex-1 px-4 py-6 space-y-2">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-cyber-primary/10 text-cyber-primary border border-cyber-primary/30'
                      : 'text-gray-400 hover:bg-cyber-bg hover:text-gray-200'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* User */}
          <div className="px-4 py-4 border-t border-cyber-border">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-200">{user?.username}</p>
                <p className="text-xs text-gray-500">{user?.role}</p>
              </div>
              <button
                onClick={logout}
                className="p-2 text-gray-400 hover:text-cyber-danger transition-colors"
              >
                <LogOut className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main className="ml-64 min-h-screen">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
