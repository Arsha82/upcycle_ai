import { useState } from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import '@fontsource/playfair-display/400.css';
import '@fontsource/playfair-display/700.css';
import '@fontsource/outfit/400.css';
import '@fontsource/outfit/500.css';
import '@fontsource/outfit/700.css';
import { Home } from './pages/Home';
import { Scanner } from './pages/Scanner';
import { Explore } from './pages/Explore';
import { Settings } from './pages/Settings';
import { ItemDetail } from './pages/ItemDetail';
import { KnowledgeBank } from './pages/KnowledgeBank';
import { FloatingChatbot } from './components/FloatingChatbot';
import { Sidebar } from './components/layout/Sidebar';
import { Header } from './components/layout/Header';
import { AnimatePresence } from 'framer-motion';

function App() {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <BrowserRouter>
      {/* Sidebar Layout */}
      <Sidebar />

      {/* Main App Container */}
      <div className="main-app-container">
        
        <Header searchQuery={searchQuery} setSearchQuery={setSearchQuery} />

        {/* Dynamic Route Content */}
        <AnimatePresence mode="wait">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/explore" element={<Explore searchQuery={searchQuery} />} />
            <Route path="/scanner" element={<Scanner />} />
            <Route path="/item/:id" element={<ItemDetail />} />
            <Route path="/kb" element={<KnowledgeBank />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </AnimatePresence>

      </div>

      {/* Global Floating Chatbot */}
      <FloatingChatbot />
    </BrowserRouter>
  )
}

export default App;

