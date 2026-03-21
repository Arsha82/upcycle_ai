import React from 'react';
import { motion } from 'framer-motion';
import { Database, Cpu, ShieldCheck, Code, Activity, Leaf } from 'lucide-react';

export const Home: React.FC = () => {
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
       opacity: 1,
       transition: { staggerChildren: 0.2 }
    }
  };

  const itemVariants: any = {
    hidden: { opacity: 0, y: 30 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.6, ease: "easeOut" } }
  };

  return (
    <div className="landing-page" style={{ padding: '2rem 3rem', overflowY: 'auto', height: '100%' }}>
      <motion.div variants={containerVariants} initial="hidden" animate="visible">
        
        {/* HERO SECTION */}
        <motion.div variants={itemVariants} className="landing-hero" style={{ textAlign: 'center', margin: '4rem 0 6rem 0' }}>
           <h1 style={{ fontSize: '3rem', fontWeight: 800, color: '#1e293b', marginBottom: '1rem', letterSpacing: '-1px' }}>
              Autonomous <span style={{ color: '#10b981' }}>Upcycling</span> Intelligence
           </h1>
           <p style={{ fontSize: '1.2rem', color: '#64748b', maxWidth: '700px', margin: '0 auto', lineHeight: '1.6' }}>
              Upcycle AI is an advanced offline-first platform powered by Local Large Language & Vision Models. It identifies raw waste materials in real-time and generates actionable DIY blueprints. Built for sustainability. Engineered for absolute privacy.
           </p>
        </motion.div>

        {/* TECH STACK SECTION */}
        <motion.div variants={itemVariants} style={{ marginBottom: '6rem' }}>
           <h2 style={{ fontSize: '1.8rem', color: '#0f172a', marginBottom: '2rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <LayersIcon /> Technology Stack
           </h2>
           <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem' }}>
              
              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                 <div style={{ padding: '12px', background: '#eff6ff', color: '#3b82f6', width: 'fit-content', borderRadius: '12px' }}><Cpu size={24}/></div>
                 <h3 style={{ fontSize: '1.2rem', color: '#1e293b' }}>Deep Learning & LLMs</h3>
                 <p style={{ color: '#64748b', fontSize: '0.9rem', lineHeight: '1.5' }}>Powered by Ollama running Llama 3.2 Vision computationally optimizing deep spatial feature extraction and robust generative context reasoning offline.</p>
              </div>

              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                 <div style={{ padding: '12px', background: '#f5f3ff', color: '#8b5cf6', width: 'fit-content', borderRadius: '12px' }}><Database size={24}/></div>
                 <h3 style={{ fontSize: '1.2rem', color: '#1e293b' }}>RAG Engine</h3>
                 <p style={{ color: '#64748b', fontSize: '0.9rem', lineHeight: '1.5' }}>ChromaDB semantic vector storage dynamically injects relevant upcycling blueprints into the LLM context limits preventing hallucinated ideas.</p>
              </div>

              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                 <div style={{ padding: '12px', background: '#ecfdf5', color: '#10b981', width: 'fit-content', borderRadius: '12px' }}><Code size={24}/></div>
                 <h3 style={{ fontSize: '1.2rem', color: '#1e293b' }}>Backend Framework</h3>
                 <p style={{ color: '#64748b', fontSize: '0.9rem', lineHeight: '1.5' }}>Python FastAPI providing lightning-fast asynchronous REST APIs to serve ML inference, history tracking, and dynamic routing securely.</p>
              </div>

              <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                 <div style={{ padding: '12px', background: '#fff1f2', color: '#f43f5e', width: 'fit-content', borderRadius: '12px' }}><ShieldCheck size={24}/></div>
                 <h3 style={{ fontSize: '1.2rem', color: '#1e293b' }}>Absolute Privacy</h3>
                 <p style={{ color: '#64748b', fontSize: '0.9rem', lineHeight: '1.5' }}>Because all models operate natively via Ollama without API integrations, personal images and workflow data never leave your local hardware.</p>
              </div>

           </div>
        </motion.div>

        {/* WORKFLOW PIPELINE (SCROLL ANIMATED) */}
        <motion.div variants={itemVariants} style={{ marginBottom: '6rem' }}>
           <h2 style={{ fontSize: '1.8rem', color: '#0f172a', marginBottom: '3rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Activity className="text-emerald-500" /> Operational Architecture
           </h2>
           
           <div style={{ position: 'relative', borderLeft: '2px dashed #cbd5e1', paddingLeft: '2.5rem', marginLeft: '1rem', display: 'flex', flexDirection: 'column', gap: '3.5rem' }}>
              
              <div style={{ position: 'relative' }}>
                 <div style={{ position: 'absolute', left: '-3.3rem', top: '0', background: '#10b981', color: 'white', width: '30px', height: '30px', borderRadius: '50%', display: 'flex', alignItems:'center', justifyContent: 'center', fontWeight: 'bold' }}>1</div>
                 <h3 style={{ fontSize: '1.3rem', color: '#1e293b', marginBottom: '0.5rem' }}>Image Acquisition & Normalization</h3>
                 <p style={{ color: '#64748b', lineHeight: '1.6', maxWidth: '800px' }}>
                    The user uploads an image of discarded materials. The React UI converts it to a binary payload and safely streams it to the FastAPI backend over HTTP dynamically handling concurrent requests via Uvicorn.
                 </p>
              </div>

              <div style={{ position: 'relative' }}>
                 <div style={{ position: 'absolute', left: '-3.3rem', top: '0', background: '#10b981', color: 'white', width: '30px', height: '30px', borderRadius: '50%', display: 'flex', alignItems:'center', justifyContent: 'center', fontWeight: 'bold' }}>2</div>
                 <h3 style={{ fontSize: '1.3rem', color: '#1e293b', marginBottom: '0.5rem' }}>Vision Heuristics & Material Extraction</h3>
                 <p style={{ color: '#64748b', lineHeight: '1.6', maxWidth: '800px' }}>
                    Instead of brittle classifiers, we pipe the image instantly to Llama 3.2 Vision via the Ollama CLI. The multimodal intelligence observes structural bounds and isolates key recognizable items embedded within your environment.
                 </p>
              </div>

              <div style={{ position: 'relative' }}>
                 <div style={{ position: 'absolute', left: '-3.3rem', top: '0', background: '#10b981', color: 'white', width: '30px', height: '30px', borderRadius: '50%', display: 'flex', alignItems:'center', justifyContent: 'center', fontWeight: 'bold' }}>3</div>
                 <h3 style={{ fontSize: '1.3rem', color: '#1e293b', marginBottom: '0.5rem' }}>Retrieval-Augmented Generation (RAG)</h3>
                 <p style={{ color: '#64748b', lineHeight: '1.6', maxWidth: '800px' }}>
                    Identified materials are queried against ChromaDB, our persistent vector store. Highly correlated community-verified tutorials and upcycling knowledge blocks are retrieved via dense embedding similarity to ground the next inference cycle.
                 </p>
              </div>

              <div style={{ position: 'relative' }}>
                 <div style={{ position: 'absolute', left: '-3.3rem', top: '0', background: '#10b981', color: 'white', width: '30px', height: '30px', borderRadius: '50%', display: 'flex', alignItems:'center', justifyContent: 'center', fontWeight: 'bold' }}>4</div>
                 <h3 style={{ fontSize: '1.3rem', color: '#1e293b', marginBottom: '0.5rem' }}>Data Visualization & Idea Synthesis</h3>
                 <p style={{ color: '#64748b', lineHeight: '1.6', maxWidth: '800px' }}>
                    The server streams standard LLM text buffers line-by-line via asynchronous Generators back to the client. Real-time metrics log the interaction to create session-proof history auditing trails inside the Explore dashboard.
                 </p>
              </div>

           </div>
        </motion.div>

        {/* DATA SET & TRAINING METRICS */}
        <motion.div variants={itemVariants} className="card primary-dark" style={{ marginBottom: '4rem', display: 'flex', gap: '3rem', flexWrap: 'wrap', backgroundColor: '#1e3a29' }}>
           <div style={{ flex: '1 1 300px' }}>
              <h2 style={{ fontSize: '1.5rem', marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'white' }}>
                 <Leaf size={24} /> Sustainable Core
              </h2>
              <p style={{ color: '#a3c2b0', lineHeight: '1.6', marginBottom: '1.5rem' }}>
                 Upcycle AI was built natively off community-harvested upcycling datasets. The RAG architecture bypasses standard LLM safety refusals on obscure tool usage, enabling highly creative, safe, and robust DIY tutorials for a circular economy.
              </p>
           </div>
           <div style={{ flex: '1 1 300px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
                 <div style={{ fontSize: '2rem', fontWeight: 700, color: '#60a5fa' }}>Ollama</div>
                 <div style={{ fontSize: '0.85rem', color: '#a3c2b0', marginTop: '0.2rem' }}>Inference Engine</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
                 <div style={{ fontSize: '2rem', fontWeight: 700, color: '#34d399' }}>100%</div>
                 <div style={{ fontSize: '0.85rem', color: '#a3c2b0', marginTop: '0.2rem' }}>Offline Execution</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
                 <div style={{ fontSize: '2rem', fontWeight: 700, color: '#f472b6' }}>0ms</div>
                 <div style={{ fontSize: '0.85rem', color: '#a3c2b0', marginTop: '0.2rem' }}>Network API Latency</div>
              </div>
              <div style={{ background: 'rgba(255,255,255,0.05)', padding: '1.5rem', borderRadius: '12px', textAlign: 'center' }}>
                 <div style={{ fontSize: '2rem', fontWeight: 700, color: '#fbbf24' }}>ChromaDB</div>
                 <div style={{ fontSize: '0.85rem', color: '#a3c2b0', marginTop: '0.2rem' }}>Semantic Vector Storage</div>
              </div>
           </div>
        </motion.div>

      </motion.div>
    </div>
  );
};

// Helper for Layers icon since we maxed our imports
const LayersIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500">
    <polygon points="12 2 2 7 12 12 22 7 12 2"></polygon>
    <polyline points="2 12 12 17 22 12"></polyline>
    <polyline points="2 17 12 22 22 17"></polyline>
  </svg>
);
