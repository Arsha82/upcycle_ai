import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, Loader2, Sparkles, X } from 'lucide-react';
import { DotLottieReact } from '@lottiefiles/dotlottie-react';

export const FloatingChatbot: React.FC = () => {
  const [isChatOpen, setIsChatOpen] = useState(false);
  const [chatInput, setChatInput] = useState('');
  const [chatLog, setChatLog] = useState<{role: 'user'|'ai', text: string}[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);

  const handleChatSend = () => {
    if (!chatInput.trim()) return;
    setChatLog(prev => [...prev, { role: 'user', text: chatInput }]);
    setChatInput('');
    setIsProcessing(true);
    setTimeout(() => {
      setChatLog(prev => [...prev, { role: 'ai', text: "I'm your global Upcycle AI assistant! Ask me about projects or anything else." }]);
      setIsProcessing(false);
    }, 1500);
  };

  return (
    <>
      <AnimatePresence>
        {!isChatOpen && (
          <motion.button
            key="chat-fab"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            transition={{ type: "spring", damping: 20, stiffness: 150 }}
            onClick={() => setIsChatOpen(true)}
            className="fixed bottom-2 right-2 md:bottom-6 md:right-6 w-40 h-40 md:w-48 md:h-48 flex items-center justify-center z-[100] cursor-pointer drop-shadow-2xl hover:drop-shadow-[0_0_25px_rgba(30,58,41,0.6)] transition-all bg-transparent border-none outline-none group"
            title="Open Upcycle AI Assistant"
          >
            {/* 
              Avoid scale animations on Lottie containers to prevent ResizeObserver 
              rendering the canvas at tiny resolutions (which causes pixelation/bad proportions).
            */}
            <div className="w-full h-full transform transition-transform duration-300 group-hover:scale-110">
              <DotLottieReact src="/Live%20chatbot.lottie" loop autoplay className="w-full h-full pointer-events-none" />
            </div>
          </motion.button>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {isChatOpen && (
          <motion.div
            key="chat-window"
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            transition={{ type: "spring", damping: 25, stiffness: 200 }}
            className="fixed bottom-6 right-6 md:bottom-10 md:right-10 w-[380px] md:w-[420px] h-[600px] glass-card flex flex-col rounded-[2.5rem] shadow-2xl z-[100] overflow-hidden border border-white/40 bg-white/80 backdrop-blur-2xl"
          >
            {/* Header */}
            <div className="flex justify-between items-center px-6 py-4 border-b border-black/10 bg-[#1e3a29]/5 backdrop-blur-md">
              <h3 className="font-bold flex items-center gap-2 uppercase tracking-widest text-[#0a100d] text-sm group cursor-default">
                <Sparkles className="w-4 h-4 text-[#1e3a29]" /> AI Assistant
              </h3>
              
              <button 
                onClick={() => setIsChatOpen(false)} 
                className="w-20 h-20 -mr-4 -my-6 transition-transform hover:-translate-y-1 cursor-pointer overflow-hidden relative flex items-center justify-center drop-shadow-md group rounded-full"
                title="Close Chat"
              >
                <div className="absolute inset-0 bg-transparent group-hover:bg-black/5 rounded-full transition-colors z-10 flex items-center justify-center">
                  <X className="w-6 h-6 text-[#1e3a29] opacity-0 group-hover:opacity-100 transition-opacity absolute" />
                </div>
                <DotLottieReact src="/Live%20chatbot.lottie" loop autoplay className="w-[120%] h-[120%] pointer-events-none" />
              </button>
            </div>
            
            <div className="flex-1 overflow-y-auto p-4 flex flex-col gap-3 scrollbar-hide">
              {chatLog.length === 0 ? (
                <div className="flex-1 flex flex-col items-center justify-center text-center opacity-80 p-4">
                  <div className="w-36 h-36 mb-2 opacity-70">
                    <DotLottieReact src="/Live%20chatbot.lottie" loop autoplay className="w-full h-full" />
                  </div>
                  <p className="text-sm text-[#0a100d] font-bold leading-relaxed max-w-[80%]">I'm your AI assistant! Ask me anything about upcycling.</p>
                </div>
              ) : (
                chatLog.map((msg, i) => (
                  <div key={i} className={`px-4 py-3 rounded-2xl max-w-[85%] text-sm font-medium ${msg.role === 'user' ? 'bg-[#1e3a29] text-white self-end rounded-br-none shadow-md' : 'bg-white text-[#2c3e34] self-start rounded-bl-none shadow-sm border border-black/5'}`}>
                    {msg.text}
                  </div>
                ))
              )}
              {isProcessing && chatLog.length > 0 && (
                <div className="self-start text-[#4a6355] text-xs font-bold animate-pulse px-2 flex items-center gap-2"><Loader2 className="w-3 h-3 animate-spin"/> Thinking...</div>
              )}
            </div>
            
            <div className="p-4 bg-black/5 backdrop-blur-md relative border-t border-black/5">
              <input 
                type="text" 
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                onKeyDown={(e) => e.key === 'Enter' && handleChatSend()}
                placeholder="Ask me anything..." 
                className="w-full pl-5 pr-12 py-3.5 rounded-2xl bg-white border border-black/10 focus:border-[#a3c2b0] focus:ring-2 focus:ring-[#a3c2b0]/30 shadow-sm text-[#0a100d] font-medium placeholder:text-gray-400 transition-all outline-none" 
              />
              <button 
                onClick={handleChatSend}
                className="absolute right-6 top-1/2 -translate-y-1/2 w-8 h-8 bg-[#1e3a29] text-white rounded-xl flex items-center justify-center hover:bg-[#111a14] transition-colors shadow-sm transform hover:scale-105"
              >
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};
