import React from 'react';
import { Home, ScanLine, PieChart, Activity, Settings as SettingsIcon, Database } from 'lucide-react';
import { useLocation, useNavigate } from 'react-router-dom';

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const currentView = location.pathname === '/' ? 'home' : 
                      location.pathname.startsWith('/explore') ? 'analytics' : 
                      location.pathname.startsWith('/scanner') ? 'scan' : 
                      location.pathname.startsWith('/kb') ? 'kb' : 
                      location.pathname.startsWith('/settings') ? 'settings' : '';

  const navItems = [
    { id: 'home', icon: Home, path: '/' },
    { id: 'analytics', icon: PieChart, path: '/explore' },
    { id: 'scan', icon: ScanLine, path: '/scanner' },
    { id: 'kb', icon: Database, path: '/kb' },
    { id: 'settings', icon: SettingsIcon, path: '/settings' }
  ];

  return (
    <aside className="sidebar">
      <div className="sidebar-logo">
        <Activity size={32} />
      </div>
      
      <div className="sidebar-nav">
        {navItems.map(item => (
          <div 
            key={item.id}
            className={`nav-item ${currentView === item.id ? 'active' : ''}`}
            onClick={() => navigate(item.path)}
            title={item.id.charAt(0).toUpperCase() + item.id.slice(1)}
          >
            <item.icon size={20} />
          </div>
        ))}
      </div>
      
      <div className="sidebar-bottom">
      </div>
    </aside>
  );
}
