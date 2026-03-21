import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, ScanLine, CheckCircle, AlertOctagon } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

export const Scanner: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [isScanning, setIsScanning] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  }

  const handleFile = (selectedFile: File) => {
    setFile(selectedFile);
    const objectUrl = URL.createObjectURL(selectedFile);
    setPreview(objectUrl);
    setResult(null);
    setError(null);
  }

  const handleScan = async () => {
    if (!file) return;
    setIsScanning(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        body: formData
      });
      const data = await response.json();
      
      // Artificial delay for UI scanning effect
      setTimeout(async () => {
         const items = data.items || ['Unknown Material'];
         
         // Now fetch generation
         try {
           const genRes = await fetch('http://localhost:8000/api/generate', {
             method: 'POST',
             headers: { 'Content-Type': 'application/json' },
             body: JSON.stringify({ items: items, equipment: "Basic household tools" })
           });
           
           if (!genRes.body) throw new Error("No body");
           
           const reader = genRes.body.getReader();
           const decoder = new TextDecoder();
           let fullText = "";
           
           setIsScanning(false);
           setResult({ items, ideas: [] });

           while (true) {
             const { done, value } = await reader.read();
             if (done) break;
             fullText += decoder.decode(value, { stream: true });
             const parsedIdeas = fullText.split('|||IDEA_SEPARATOR|||').map((s: string) => s.trim()).filter((s: string) => s.length > 0);
             if (parsedIdeas.length > 0) {
               setResult({ items, ideas: parsedIdeas });
             }
           }
         } catch(e) {
            setIsScanning(false);
            setError("Failed to generate blueprints.");
         }
         
      }, 1500)

    } catch (err) {
      setTimeout(() => {
        setIsScanning(false);
        setError('Failed to connect to local vision model. Is Ollama running?');
      }, 1000)
    }
  }

  return (
    <div className="scanner-layout dashboard-content">
      <AnimatePresence mode="wait">
        {!preview ? (
          <motion.div 
            key="upload"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, y: -20 }}
            className="upload-panel"
            onDragOver={handleDragOver}
            onDrop={handleDrop}
          >
            <input 
              type="file" 
              id="file-upload" 
              style={{ display: 'none' }} 
              accept="image/*" 
              onChange={handleFileSelect} 
            />
            <label htmlFor="file-upload" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem', cursor: 'pointer' }}>
              <Upload size={64} color="#9ca3af" strokeWidth={1} />
              <div style={{ textAlign: 'center' }}>
                <h2 style={{ fontSize: '1.2rem', fontWeight: 600, color: '#1e293b' }}>DROP WASTE IMAGE HERE</h2>
                <p style={{ color: '#64748b' }}>High-resolution JPG/PNG accepted</p>
              </div>
            </label>
          </motion.div>
        ) : (
          <motion.div 
            key="interface"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="scan-interface"
          >
            <div className={`image-dock ${isScanning ? 'scanning-active' : ''}`}>
              <img src={preview} alt="Target" className="preview-image" />
              
              {isScanning && (
                <>
                  <motion.div 
                    className="laser-line bg-[#10b981]"
                    initial={{ top: 0 }}
                    animate={{ top: "100%" }}
                    transition={{ 
                      duration: 2, 
                      repeat: Infinity, 
                      ease: "linear",
                      repeatType: "reverse"
                    }}
                  />
                </>
              )}
            </div>

            <div className="process-column">
            {result && (
              <motion.div 
                className="result-card"
                initial={{ opacity: 0, x: 20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.5, type: "spring" }}
              >
                <div className="status-header real" style={{ background: '#10b981' }}>
                  <CheckCircle size={40}/>
                  <div style={{ marginLeft: '1rem' }}>
                    <h2 style={{ fontSize: '1.5rem', fontWeight: 700 }}>Material Identified</h2>
                    <h3 style={{ fontSize: '1rem', opacity: 0.9 }}>{result.items.join(', ')}</h3>
                  </div>
                </div>

                {result.ideas.length > 0 && (
                  <div className="prose prose-lg max-w-none font-sans bg-white p-6 rounded-2xl border border-gray-200 mt-4 shadow-sm h-[400px] overflow-y-auto">
                    <ReactMarkdown
                      components={{
                        h2: ({node, ...props}: any) => <h2 className="text-2xl font-bold text-[#1e3a29] border-b border-black/10 pb-2 mb-4" {...props} />,
                        h3: ({node, ...props}: any) => <h3 className="text-lg font-bold uppercase text-[#0a100d] mb-3 mt-6" {...props} />,
                        strong: ({node, ...props}: any) => <strong className="font-extrabold text-[#1e3a29]" {...props} />,
                        ul: ({node, ...props}: any) => <ul className="list-disc ml-6 mb-6 space-y-1 text-gray-700" {...props} />,
                        p: ({node, ...props}: any) => <p className="mb-4 text-gray-700" {...props} />,
                        ol: ({node, ...props}: any) => <ol className="list-decimal marker:font-bold ml-6 mb-6 space-y-2 text-gray-700" {...props} />,
                      }}
                    >
                      {result.ideas[0]}
                    </ReactMarkdown>
                  </div>
                )}
              </motion.div>
            )}

            <div className="actions" style={{ marginTop: '2rem', display: 'flex', gap: '1rem' }}>
              {!isScanning && !result && !error && (
                <button className="cyber-btn" onClick={handleScan}>
                  <ScanLine size={18} /> Process Validation
                </button>
              )}
              
              {(result || error || !isScanning) && preview && (
                <button className="cyber-btn secondary" onClick={() => { setPreview(null); setFile(null); setResult(null); setError(null); }}>
                   Upload Different Subject
                </button>
              )}
            </div>
            
          </div>

            {error && (
               <motion.div initial={{opacity:0, scale:0.95}} animate={{opacity:1, scale:1}} style={{ background: '#fef2f2', border: '1px solid #fecaca', padding: '1.5rem', borderRadius: '16px', display: 'flex', alignItems: 'center', gap: '1rem', color: '#ef4444' }}>
                  <AlertOctagon size={24} />
                  <p style={{ fontWeight: 500 }}>{error}</p>
               </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

