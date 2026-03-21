import { useBgModeStore } from './bgModeStore';
import { BrowserRouter, Routes, Route, Link } from 'react-router-dom';
import '@fontsource/playfair-display/400.css';
import '@fontsource/playfair-display/700.css';
import '@fontsource/outfit/400.css';
import '@fontsource/outfit/500.css';
import '@fontsource/outfit/700.css';
import { BackgroundEngine } from './components/layout/BackgroundEngine';
import { Home } from './pages/Home';
import { Scanner } from './pages/Scanner';
import { ItemDetail } from './pages/ItemDetail';
import { KnowledgeBank } from './pages/KnowledgeBank';
import { Leaf, Wind, Trees, Database } from 'lucide-react';

function App() {
  const bgMode = useBgModeStore((state: any) => state.bgMode);
  const toggleBgMode = useBgModeStore((state: any) => state.toggleBgMode);

  return (
    <BrowserRouter>
      {/* Background Layer */}
      <BackgroundEngine />

      {/* Modern Frosted Navbar */}
      <nav className="fixed top-0 w-full z-50 px-6 py-4 flex justify-between items-center bg-white/70 #0a100d]/70 backdrop-blur-xl border-b border-black/5  transition-colors duration-700">
        <Link to="/" className="flex items-center gap-2 group cursor-pointer">
          <div className="p-2 bg-[#1e3a29]/80 backdrop-blur-md border border-white/20 shadow-[0_8px_32px_rgba(30,58,41,0.3)] text-white rounded-lg group-hover:bg-[#1b4332]/90 :bg-[#a3c2b0]/90 :text-[#0c1a10] transition-all">
            <Leaf className="w-5 h-5" />
          </div>
          <span className="font-serif font-bold text-2xl tracking-tighter text-[#0c1a10]  drop-shadow-sm">Upcycle AI</span>
        </Link>
        
        {/* Right side controls */}
        <div className="flex items-center gap-3">
          
          <Link to="/kb" className="px-4 py-2 rounded-full flex items-center gap-2 font-sans font-semibold text-xs uppercase tracking-widest transition-all duration-300 shadow-sm backdrop-blur-sm border bg-white/60 border-black/15 text-[#0a100d] hover:bg-white/90">
            <Database className="w-4 h-4" />
            <span className="hidden sm:inline">Knowledge Bank</span>
          </Link>

          {/* Background Mode Toggle */}
          <button 
            onClick={toggleBgMode}
            title={bgMode === 'lottie' ? 'Switch to Vanta Birds' : 'Switch to Nature Lottie'}
            className={`px-4 py-2 rounded-full flex items-center gap-2 font-sans font-semibold text-xs uppercase tracking-widest transition-all duration-300 shadow-md backdrop-blur-sm border bg-white/60 border-black/15 text-[#0a100d] hover:bg-white/90`}
          >
            {bgMode === 'lottie' ? <Wind className="w-4 h-4" /> : <Trees className="w-4 h-4" />}
            <span className="hidden sm:inline">{bgMode === 'lottie' ? 'Birds' : 'Nature'}</span>
          </button>
        </div>
      </nav>

      {/* Main Routing Content */}
      <main className="w-full relative z-10 transition-colors duration-500 min-h-screen">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/scanner" element={<Scanner />} />
          <Route path="/item/:id" element={<ItemDetail />} />
          <Route path="/kb" element={<KnowledgeBank />} />
        </Routes>
      </main>
    </BrowserRouter>
  )
}

export default App;

