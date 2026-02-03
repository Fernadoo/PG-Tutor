import { Outlet, NavLink, useNavigate } from 'react-router-dom';
import { 
  BookOpen, 
  BarChart3, 
  Share2, 
  History, 
  LogOut, 
  Brain,
  Menu,
  X
} from 'lucide-react';
import { useState } from 'react';
import { useStore } from '@/store';

export default function Layout() {
  const navigate = useNavigate();
  const { reset, session } = useStore();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const handleLogout = () => {
    reset();
    navigate('/setup');
  };

  const navItems = [
    { to: '/lesson', icon: BookOpen, label: 'Lesson' },
    { to: '/progress', icon: BarChart3, label: 'Progress' },
    { to: '/graph', icon: Share2, label: 'Knowledge Graph' },
    { to: '/history', icon: History, label: 'History' },
  ];

  return (
    <div className="min-h-screen flex">
      <aside className={`
        fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-gray-200 
        transform transition-transform duration-300 ease-in-out
        lg:translate-x-0 lg:static
        ${isMobileMenuOpen ? 'translate-x-0' : '-translate-x-full'}
      `}>
        <div className="h-full flex flex-col">
          <div className="p-6 border-b border-gray-200">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary-600 rounded-xl flex items-center justify-center">
                <Brain className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-gray-900">AI Tutor</h1>
                <p className="text-xs text-gray-500">Bayesian Learning</p>
              </div>
            </div>
          </div>

          <nav className="flex-1 p-4 space-y-1">
            {navItems.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                onClick={() => setIsMobileMenuOpen(false)}
                className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
              >
                <item.icon className="w-5 h-5" />
                {item.label}
              </NavLink>
            ))}
          </nav>

          {session && (
            <div className="p-4 border-t border-gray-200">
              <div className="mb-4 p-3 bg-primary-50 rounded-lg">
                <div className="text-sm font-medium text-primary-900">
                  Mode: {session.mode === 'llm' ? 'LLM' : 'Simple'}
                </div>
                <div className="text-xs text-primary-700 mt-1">
                  Accuracy: {(session.accuracy * 100).toFixed(1)}%
                </div>
                <div className="text-xs text-primary-700">
                  Questions: {session.total_answered}
                </div>
              </div>
              
              <button
                onClick={handleLogout}
                className="w-full flex items-center gap-2 px-4 py-2 text-red-600 rounded-lg hover:bg-red-50 transition-colors"
              >
                <LogOut className="w-4 h-4" />
                End Session
              </button>
            </div>
          )}
        </div>
      </aside>

      {isMobileMenuOpen && (
        <div 
          className="fixed inset-0 bg-black/50 z-40 lg:hidden"
          onClick={() => setIsMobileMenuOpen(false)}
        />
      )}

      <div className="flex-1 flex flex-col min-w-0">
        <header className="lg:hidden bg-white border-b border-gray-200 p-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Brain className="w-6 h-6 text-primary-600" />
            <span className="font-bold text-gray-900">AI Tutor</span>
          </div>
          <button
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
            className="p-2 text-gray-600 hover:bg-gray-100 rounded-lg"
          >
            {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </header>

        <main className="flex-1 p-4 lg:p-8 overflow-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
