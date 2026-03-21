import React, { useState, useEffect } from 'react';
import { Search } from 'lucide-react';

interface HeaderProps {
  searchQuery?: string;
  setSearchQuery?: (q: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ searchQuery, setSearchQuery }) => {
  const [today, setToday] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setToday(new Date()), 60000);
    return () => clearInterval(timer);
  }, []);

  const getGreeting = () => {
    const hour = today.getHours();
    if (hour >= 5 && hour < 12) return "Good Morning";
    if (hour >= 12 && hour < 17) return "Good Afternoon";
    if (hour >= 17 && hour < 22) return "Good Evening";
    return "Night Owl mode activated";
  };

  const dateStr = today.toLocaleDateString('en-GB', { day: 'numeric', month: 'long', year: 'numeric' });
  const timeStr = today.toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

  return (
    <div className="header">
      <div className="header-top">
        <div className="search-bar">
          <Search size={18} />
          <input 
            type="text" 
            placeholder="Search blueprints, ideas, history..." 
            value={searchQuery || ''}
            onChange={(e) => setSearchQuery && setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      <div className="greeting-section">
        <h1 className="greeting-title">{getGreeting()}, Creator</h1>
        <div className="greeting-date">
          {dateStr} &nbsp;&nbsp;&nbsp; {timeStr}
        </div>
      </div>
    </div>
  );
}
