import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Sparkles, CalendarDays, Loader2, Image as ImageIcon } from 'lucide-react';
import { useNavigate, useParams } from 'react-router-dom';
import ReactMarkdown from 'react-markdown';

export const ItemDetail: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  
  const [item, setItem] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`http://localhost:8000/api/history/${id}`)
      .then(res => {
        if (!res.ok) throw new Error("Item not found");
        return res.json();
      })
      .then(data => {
        setItem(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen pt-32 flex items-center justify-center">
        <Loader2 className="w-12 h-12 text-[#a3c2b0] animate-spin" />
      </div>
    );
  }

  if (!item) {
    return (
      <div className="min-h-screen pt-32 px-12 text-center text-white font-serif text-2xl">
        Item not found in the database.
      </div>
    );
  }

  // Pre-process response to remove system conversational fillers
  const rawResponse = item.response || "";
  const cleanedResponse = rawResponse
    .replace(/.*\[CACHE HIT\].*\n?/ig, '')
    .replace(/^We instantly recognized this item from our Knowledge Base!/img, '')
    .replace(/^# Upcycling Genius Unleashed!/img, '')
    .trim();

  return (
    <div className="min-h-screen relative w-full flex flex-col md:flex-row bg-transparent">
      <div className="fixed inset-0 bg-white/60 backdrop-blur-md pointer-events-none z-0" />

      {/* FIXED LEFT PANE (Desktop Only) / Top Image (Mobile) */}
      <div className="w-full md:w-5/12 lg:w-[45%] md:fixed md:left-0 md:top-0 md:h-screen z-20 flex flex-col relative px-6 md:px-12 pt-32 md:pt-0 md:justify-center border-b md:border-b-0 md:border-r border-black/5 bg-transparent">
         
         {/* Back Button */}
         <div className="md:absolute top-8 md:top-32 left-6 lg:left-12 mb-8 md:mb-0 z-30">
           <motion.button 
             initial={{ opacity: 0, x: -20 }}
             animate={{ opacity: 1, x: 0 }}
             onClick={() => navigate(-1)}
             className="flex items-center gap-2 text-[#0a100d]/60 hover:text-[#0a100d] transition-colors w-fit font-sans uppercase tracking-[0.2em] text-xs font-semibold backdrop-blur-md bg-white/40 md:bg-transparent px-4 py-2 md:px-0 md:py-0 rounded-full md:rounded-none border border-black/5 md:border-none"
           >
             <ArrowLeft className="w-4 h-4" /> Back to Gallery
           </motion.button>
         </div>

         {/* Giant Image Wrapper */}
         <div className="flex-1 w-full flex items-center justify-center pointer-events-none md:mt-24 lg:mt-16">
           <motion.div 
             initial={{ opacity: 0, scale: 0.95 }}
             animate={{ opacity: 1, scale: 1 }}
             transition={{ delay: 0.2 }}
             className="w-full relative shadow-[0_30px_80px_rgba(0,0,0,0.15)] rounded-[2.5rem] overflow-hidden border border-black/10 group mb-12 md:mb-0 pointer-events-auto bg-white/60 backdrop-blur-2xl p-4 md:p-6 glass-card"
           >
              <div className="w-full h-[20rem] md:h-[28rem] lg:h-[38rem] rounded-[1.5rem] overflow-hidden bg-gray-100 flex justify-center items-center relative z-10">
                {item.image_url ? (
                  <img 
                    src={item.image_url} 
                    alt="Original Image" 
                    className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000 ease-out"
                  />
                ) : (
                  <ImageIcon className="w-16 h-16 text-black/10"/>
                )}
              </div>
              <p className="text-center text-[#0a100d]/50 text-[10px] tracking-[0.4em] uppercase font-sans mt-5 mb-1 relative z-10 font-medium">Original Capture</p>
           </motion.div>
         </div>
      </div>

      {/* SCROLLING RIGHT PANE (Markdown Text) */}
      <div className="w-full md:w-7/12 lg:w-[55%] md:ml-auto z-10 flex flex-col px-6 md:px-16 lg:px-24 pt-12 pb-32">
         
         {/* Title Block */}
         <motion.div 
           initial={{ opacity: 0, y: 20 }}
           animate={{ opacity: 1, y: 0 }}
           className="mb-16 mt-8"
         >
           <h1 className="font-serif text-5xl md:text-6xl lg:text-7xl font-bold text-[#0a100d] mb-6 tracking-tight capitalize leading-tight">Saved:<br/>{item.title || "Scanned Item"}</h1>
           <div className="flex items-center gap-6 text-[#0a100d]/60 font-sans text-xs tracking-widest uppercase">
             <span className="flex items-center gap-2"><CalendarDays className="w-4 h-4" /> {item.timestamp || "Unknown Date"}</span>
             <span className="flex items-center gap-2 text-[#1e3a29]"><Sparkles className="w-4 h-4" /> Saved Object</span>
           </div>
         </motion.div>

         {/* Markdown Block */}
         <motion.div 
           initial={{ opacity: 0, x: 30 }}
           animate={{ opacity: 1, x: 0 }}
           transition={{ delay: 0.3 }}
           className="glass-card bg-white/70 backdrop-blur-xl p-8 md:p-12 lg:p-16 rounded-[3rem] border border-black/5 shadow-xl"
         >
            <div className="max-w-none font-sans flex flex-col pt-2">
              <ReactMarkdown 
                components={{
                  h1: ({node, ...props}: any) => <h1 className="font-serif text-4xl lg:text-5xl text-[#0a100d] tracking-tight mb-10 mt-16 pb-4 border-b border-black/10 leading-snug" {...props} />,
                  h2: ({node, ...props}: any) => <h2 className="font-serif text-3xl lg:text-4xl text-[#0a100d] tracking-tight mb-8 mt-12 pb-3 border-b border-black/10 leading-snug" {...props} />,
                  h3: ({node, ...props}: any) => <h3 className="font-sans text-xl lg:text-2xl text-[#1e3a29] tracking-[0.2em] uppercase mt-12 mb-6 font-bold" {...props} />,
                  p: ({node, ...props}: any) => <p className="mb-6 text-[#0a100d]/80 text-[1.1rem] lg:text-[1.2rem] leading-relaxed tracking-wide" {...props} />,
                  ul: ({node, ...props}: any) => <ul className="list-disc ml-8 mb-8 text-[#0a100d]/80 space-y-3 text-[1.1rem] lg:text-[1.2rem] marker:text-[#1e3a29]/50" {...props} />,
                  ol: ({node, ...props}: any) => <ol className="list-decimal ml-8 mb-8 text-[#0a100d]/80 space-y-3 text-[1.1rem] lg:text-[1.2rem] marker:text-[#1e3a29]/50 font-serif" {...props} />,
                  li: ({node, ...props}: any) => <li className="leading-relaxed pl-3" {...props} />,
                  strong: ({node, ...props}: any) => <strong className="font-extrabold text-[#1e3a29] tracking-wide" {...props} />,
                  a: ({node, ...props}: any) => <a className="text-[#1e3a29] hover:text-[#0a100d] underline decoration-[#1e3a29]/30 hover:decoration-[#0a100d]/60 underline-offset-[6px] transition-all" {...props} />,
                  blockquote: ({node, ...props}: any) => <blockquote className="border-l-[3px] border-[#1e3a29] bg-[#1e3a29]/5 rounded-r-2xl p-6 italic text-[#0a100d]/70 my-8 shadow-inner" {...props} />,
                  code: ({node, inline, ...props}: any) => 
                    inline 
                      ? <code className="bg-black/5 text-[#1e3a29] px-2 py-1 rounded-md font-mono text-[0.9em] shadow-sm font-bold" {...props} />
                      : <code className="block bg-gray-50 p-6 lg:p-8 rounded-3xl text-[#0a100d]/80 font-mono text-sm my-8 overflow-x-auto border border-black/5 shadow-inner" {...props} />
                }}
              >
                {cleanedResponse}
              </ReactMarkdown>
            </div>
         </motion.div>
      </div>
    </div>
  );
};
