import React, { useEffect, useState, useRef } from 'react';
import { motion, useScroll } from 'framer-motion';
import { Zap, Brain, BadgeDollarSign, Image as ImageIcon, ArrowRight, Loader2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { HeroTitle3D } from '../components/HeroTitle3D';
import ReactMarkdown from 'react-markdown';

export const Home: React.FC = () => {
  const navigate = useNavigate();

  const [dbItems, setDbItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/api/history')
      .then(res => res.json())
      .then(data => {
        setDbItems(data);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to fetch history:", err);
        setLoading(false);
      });
  }, []);

  const scrollRef = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ container: scrollRef });

  return (
    <div ref={scrollRef} className="w-full h-screen overflow-y-scroll bg-transparent text-[#0a100d]  font-sans scrollbar-hide">
      
      {/* 
        HERO SLIDE
        Contains the brand, features (on top), and call to action. 
      */}
      <section className="relative w-full h-screen flex flex-col justify-center items-center overflow-hidden pt-20">
        
        {/* Soft gradient blend for text readability against global background */}
        <div className="absolute inset-0 bg-gradient-to-t from-white/80 via-transparent to-white/30 #0a100d]/80  #0a100d]/30 pointer-events-none z-0 transition-colors duration-700" />

        <div className="relative z-10 text-center w-full max-w-[90vw] xl:max-w-7xl mx-auto px-4 flex flex-col items-center">
          <HeroTitle3D scrollY={scrollYProgress} />
          
          <button 
            onClick={() => navigate('/scanner')}
            className="relative z-30 -mt-12 md:-mt-24 lg:-mt-32 group px-8 py-4 bg-[#1e3a29]/80 backdrop-blur-md border border-white/20 shadow-[0_8px_32px_rgba(30,58,41,0.3)] text-white rounded-full font-bold uppercase tracking-widest hover:bg-[#1b4332]/90 dark:hover:bg-[#a3c2b0]/90 dark:hover:text-[#0a100d] transition-all flex items-center gap-3 mb-16"
          >
            Start Scanning
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>

          {/* Feature Things On Top */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 w-full">
            <FeatureCard icon={<Zap/>} title="Fully Offline" desc="Runs locally with ZERO API dependence." />
            <FeatureCard icon={<Brain/>} title="RAG Grounded" desc="Context-aware from embedded upcycle datasets." />
            <FeatureCard icon={<BadgeDollarSign/>} title="Zero Cost" desc="No subscriptions. 100% free open-source AI." />
          </div>
          
          <p className="mt-12 reactive-text font-bold text-[1rem] tracking-[0.3em] uppercase animate-bounce">Scroll to view History ↓</p>
        </div>
      </section>

      {/* 
        DATABASE FULL-SCREEN CARDS 
        Iterating over history items
      */}
      {loading ? (
        <section className="relative w-full h-screen flex items-center justify-center p-4">
          <Loader2 className="w-12 h-12 text-[#1e3a29] #a3c2b0] animate-spin" />
        </section>
      ) : dbItems.length === 0 ? (
        <section className="relative w-full h-screen flex items-center justify-center p-4">
          <p className="text-[#0a100d]/60  font-sans font-bold tracking-widest uppercase">No history items found. Go scan something!</p>
        </section>
      ) : (
        dbItems.map((item) => {
          // Santize and format the logic for text presentation
          const cleanDesc = (item.desc || "").replace(/.*\[CACHE HIT\].*\n?/ig, '').replace(/⚡/g, '').trim();
          const firstIdea = (item.details || "").split('\n').find((line: string) => line.length > 20) || "AI-generated upcycled creation.";
          const displayDesc = cleanDesc || firstIdea;

          return (
          <section key={item.id} className="relative w-full h-screen flex items-center justify-center p-4 md:p-12">
            
            {/* Subtle overlay for the specific slide to pop the card out */}
            <div className="absolute inset-0 bg-white/60 #0a100d]/60 pointer-events-none z-0 transition-colors duration-700" />

            {/* Massive Glassmorphism Layout Container */}
            <motion.div 
               initial={{ opacity: 0, scale: 0.95 }}
               whileInView={{ opacity: 1, scale: 1 }}
               viewport={{ margin: "-100px", once: false }}
               transition={{ duration: 0.8, ease: "easeOut" }}
               className="relative z-10 w-full max-w-7xl h-full max-h-[85vh] rounded-[2.5rem] glass-card flex flex-col overflow-hidden p-2"
            >
               
               {/* Simple Top Navigation inside Card */}
               <div className="flex justify-between items-center p-8 md:px-12 md:pt-10">
                 <div className="flex items-center gap-6">
                   <span className="font-bold text-xl tracking-wide text-[#0a100d] ">History</span>
                   <span className="px-4 py-1.5 rounded-full border border-black/20  text-sm font-bold  hover:bg-black/5 :bg-white/10 transition-colors cursor-pointer text-[#0a100d]/90 ">Upcycled Details</span>
                 </div>
                 <div className="flex gap-1.5 opacity-60">
                   <div className="w-1.5 h-1.5 rounded-full bg-[#0a100d] "/>
                   <div className="w-1.5 h-1.5 rounded-full bg-[#0a100d] "/>
                   <div className="w-1.5 h-1.5 rounded-full bg-[#0a100d] "/>
                 </div>
               </div>

               {/* Content Layout Area */}
               <div className="flex-1 flex flex-col md:flex-row px-8 md:px-12 pt-4 pb-12 gap-12 md:gap-8 overflow-y-auto scrollbar-hide">
                  
                  {/* Left Side: Massive Title and Description */}
                  <div className="flex-1 flex flex-col justify-center">
                     <h2 className="font-sans font-extrabold text-5xl md:text-7xl mb-6 leading-[1.1] tracking-tight">
                       {item.title}
                     </h2>
                     <p className="opacity-80 text-lg md:text-xl font-bold leading-relaxed max-w-md font-sans">
                       {displayDesc}
                     </p>
                  </div>

                  {/* Right Side: Details and Scanned Showcase */}
                  <div className="flex-1 flex flex-col justify-center md:pl-16">
                     <h3 className="font-extrabold text-xl mb-4 uppercase tracking-widest border-b border-current pb-2 w-max opacity-90">Details</h3>
                     <div className="opacity-80 font-medium text-base font-sans mb-10 max-h-[30vh] overflow-y-auto pr-4 scrollbar-hide">
                       <ReactMarkdown 
                         components={{
                           h1: ({node, ...props}: any) => <h1 className="font-serif text-xl font-bold mb-4" {...props} />,
                           h2: ({node, ...props}: any) => <h2 className="font-serif text-lg font-bold mb-3" {...props} />,
                           h3: ({node, ...props}: any) => <h3 className="font-sans text-md font-bold mb-2 uppercase tracking-wide text-[#1e3a29]" {...props} />,
                           p: ({node, ...props}: any) => <p className="mb-4 leading-relaxed" {...props} />,
                           ul: ({node, ...props}: any) => <ul className="list-disc ml-6 mb-4 space-y-1" {...props} />,
                           ol: ({node, ...props}: any) => <ol className="list-decimal ml-6 mb-4 space-y-1" {...props} />,
                           li: ({node, ...props}: any) => <li className="leading-relaxed" {...props} />,
                           strong: ({node, ...props}: any) => <strong className="font-bold text-[#1e3a29] tracking-wide" {...props} />,
                         }}
                       >
                         {item.details?.replace(/.*\[CACHE HIT\].*\n?/ig, '').replace(/⚡/g, '').trim()}
                       </ReactMarkdown>
                     </div>

                     <h3 className="font-extrabold text-xl mb-6 uppercase tracking-widest border-b border-current pb-2 w-max opacity-90">Scanned Source</h3>
                     <div className="w-[180px] h-[180px] rounded-3xl overflow-hidden shadow-[0_10px_30px_rgba(0,0,0,0.5)] border border-white/30 mb-8 cursor-pointer group inline-block bg-black/20 p-1">
                        {item.bgImage ? (
                          <img src={item.bgImage} alt="Scanned Raw Data" className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700 ease-out" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center text-black/20 "><ImageIcon className="w-8 h-8"/></div>
                        )}
                     </div>

                     <button 
                       onClick={() => navigate(`/item/${item.id}`)}
                       className="px-8 py-4 bg-black/5  hover:bg-black hover:text-white :bg-white text-[#0a100d]  :text-[#090d0b] border border-black/20  rounded-full font-bold uppercase tracking-[0.2em] transition-all duration-300 w-fit flex items-center gap-3 backdrop-blur-md shadow-lg hover:shadow-xl mt-auto"
                     >
                       Learn More <ArrowRight className="w-5 h-5" />
                     </button>
                  </div>
               </div>

            </motion.div>

          </section>
          );
        })
      )}
      
    </div>
  );
};

const FeatureCard = ({ icon, title, desc }: { icon: React.ReactNode, title: string, desc: string }) => (
  <div className="glass-card flex flex-col items-center text-center p-6 transition-all duration-700">
    <div className="p-4 bg-[#1e3a29]/80 backdrop-blur-md border border-white/20 shadow-[0_8px_32px_rgba(30,58,41,0.3)] text-white #a3c2b0] rounded-full mb-4">
      {icon}
    </div>
    <h4 className="font-extrabold text-2xl mb-2">{title}</h4>
    <p className="opacity-80 font-bold text-[0.95rem]">{desc}</p>
  </div>
);

