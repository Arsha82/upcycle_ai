import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { UploadCloud, Camera, Hammer, ArrowRight, ArrowLeft, Loader2, Sparkles, History as HistoryIcon, Trash2, Edit2 } from 'lucide-react';
import ReactMarkdown from 'react-markdown';

type Step = 1 | 2 | 3;

export const Scanner: React.FC = () => {
  const [step, setStep] = useState<Step>(1);
  const [isDragging, setIsDragging] = useState(false);
  const [visionItems, setVisionItems] = useState<string[]>([]);
  const [selectedItems, setSelectedItems] = useState<string[]>([]);
  const [tools, setTools] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [generatedIdeas, setGeneratedIdeas] = useState<string[]>([]);
  const [currentIdeaIndex, setCurrentIdeaIndex] = useState(0);
  const [_selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      performVisionScan(e.dataTransfer.files[0]);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      performVisionScan(e.target.files[0]);
    }
  };

  const performVisionScan = async (file: File) => {
    setSelectedFile(file);
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      const res = await fetch('http://localhost:8000/api/scan', {
        method: 'POST',
        body: formData
      });
      
      const data = await res.json();
      if (data.items && data.items.length > 0) {
        setVisionItems(data.items);
        setSelectedItems(data.items); // Select all by default
      } else {
        // Fallback robustly
        setVisionItems(['Unidentifiable Material']);
        setSelectedItems(['Unidentifiable Material']);
      }
      setIsProcessing(false);
      setStep(2);
    } catch(err) {
      console.error(err);
      setIsProcessing(false);
      alert('Failed to connect to local vision model. Is Ollama running?');
    }
  };

  const performGeneration = async () => {
    setIsProcessing(true);
    setGeneratedIdeas([]);
    setCurrentIdeaIndex(0);
    setStep(3); // Enter Step 3 immediately to show loading UI
    
    try {
      const res = await fetch('http://localhost:8000/api/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ items: selectedItems, equipment: tools })
      });
      
      if (!res.body) throw new Error("No response body");
      
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let fullText = "";
      
      setIsProcessing(false); // Disable top-level processing, text is streaming now
      
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        
        fullText += decoder.decode(value, { stream: true });
        
        // Split by the explicit delimiter defined in inference.py
        const parsedIdeas = fullText.split('|||IDEA_SEPARATOR|||').map(s => s.trim()).filter(s => s.length > 0);
        
        if (parsedIdeas.length > 0) {
          setGeneratedIdeas(parsedIdeas);
        }
      }
    } catch (err) {
      console.error(err);
      setIsProcessing(false);
      alert('Generation failed. Is Ollama running locally?');
    }
  };

  return (
    <div className="min-h-screen pt-32 pb-20 px-4 md:px-8 max-w-7xl mx-auto flex flex-col md:flex-row gap-8">
      
      {/* Left Column: Interactive Scanner */}
      <motion.div 
        initial={{ opacity: 0, x: -30 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full md:w-2/3 flex flex-col"
      >
        <div className="glass-card p-8 md:p-12 relative overflow-hidden">
          
          <AnimatePresence mode="wait">
            
            {/* STEP 1: UPLOAD */}
            {step === 1 && (
              <motion.div 
                key="step1"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex flex-col items-center text-center"
              >
                <div className="w-16 h-16 bg-eco-primary/10 text-eco-primary rounded-full flex items-center justify-center mb-6">
                  <Camera className="w-8 h-8" />
                </div>
                <h2 className="font-serif text-3xl font-bold mb-2">Scan Your Waste</h2>
                <p className="text-gray-500 mb-8 font-sans">Upload a photo to let Upcycle AI identify raw materials autonomously.</p>
                
                <div 
                  className={`w-full border-2 border-dashed rounded-2xl p-12 transition-colors cursor-pointer group flex flex-col items-center justify-center bg-white/30 backdrop-blur-sm ${isDragging ? 'border-eco-primary bg-eco-primary/10' : 'border-gray-300 hover:border-eco-primary'}`}
                  onDragOver={handleDragOver}
                  onDragLeave={handleDragLeave}
                  onDrop={handleDrop}
                  onClick={() => document.getElementById('fileUpload')?.click()}
                >
                  <input 
                    id="fileUpload" 
                    type="file" 
                    accept="image/*" 
                    className="hidden" 
                    onChange={handleFileSelect} 
                  />
                  {isProcessing ? (
                    <Loader2 className="w-12 h-12 text-eco-primary animate-spin mb-4" />
                  ) : (
                    <UploadCloud className="w-12 h-12 text-gray-400 group-hover:text-eco-primary transition-colors mb-4" />
                  )}
                  <span className="font-sans font-medium text-gray-600 ">
                    {isProcessing ? "Analyzing Local Vision Model..." : "Drag & Drop or Click to Upload"}
                  </span>
                </div>
              </motion.div>
            )}

            {/* STEP 2: REFINE */}
            {step === 2 && (
              <motion.div 
                key="step2"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex flex-col"
              >
                <h2 className="font-serif text-3xl font-bold mb-2">Identified Materials</h2>
                <p className="text-gray-500 mb-6 font-sans">We found these in your image. Uncheck what you don't want to use.</p>
                
                <div className="space-y-3 mb-8">
                  {visionItems.map((item, idx) => (
                    <label key={idx} className="flex items-center gap-4 p-4 rounded-xl border border-gray-200  bg-white/50  cursor-pointer hover:bg-white/80 transition-colors">
                      <input 
                        type="checkbox" 
                        className="w-5 h-5 rounded text-eco-primary focus:ring-eco-primary"
                        checked={selectedItems.includes(item)}
                        onChange={(e) => {
                          if (e.target.checked) setSelectedItems([...selectedItems, item]);
                          else setSelectedItems(selectedItems.filter(i => i !== item));
                        }}
                      />
                      <span className="font-medium text-lg text-eco-dark ">{item}</span>
                    </label>
                  ))}
                </div>

                <div className="mb-8">
                  <label className="flex items-center gap-2 font-bold mb-3 text-eco-dark  uppercase tracking-wider text-sm">
                    <Hammer className="w-4 h-4" /> Available Tools
                  </label>
                  <input 
                    type="text" 
                    value={tools}
                    onChange={(e) => setTools(e.target.value)}
                    placeholder="e.g. Hot glue gun, scissors, paint..." 
                    className="w-full px-4 py-3 rounded-lg bg-white/50  border border-gray-200  focus:outline-none focus:ring-2 focus:ring-eco-primary text-eco-dark "
                  />
                </div>

                <div className="flex gap-4 mt-auto">
                  <button onClick={() => setStep(1)} className="px-6 py-3 rounded-lg font-bold border border-gray-300  hover:bg-gray-100 :bg-gray-800 transition-colors text-eco-dark  flex-1">Back</button>
                  <button 
                    onClick={performGeneration}
                    disabled={isProcessing || selectedItems.length === 0}
                    className="px-6 py-3 rounded-lg font-bold bg-eco-primary text-white hover:bg-[#1b4332] transition-colors flex-[2] flex justify-center items-center gap-2 disabled:opacity-50"
                  >
                    {isProcessing ? <Loader2 className="w-5 h-5 animate-spin" /> : <><Sparkles className="w-5 h-5"/> Generate Idea</>}
                  </button>
                </div>
              </motion.div>
            )}

            {/* STEP 3: RESULT */}
            {step === 3 && (
              <motion.div 
                key="step3"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="flex flex-col"
              >
                <div className="flex justify-between items-center mb-6">
                  <h2 className="font-serif text-3xl font-bold text-eco-primary flex items-center gap-3">
                    <Sparkles className="w-6 h-6" /> Generated Ideas
                  </h2>
                  <div className="flex items-center gap-3">
                    <button 
                      onClick={() => setCurrentIdeaIndex(Math.max(0, currentIdeaIndex - 1))}
                      disabled={currentIdeaIndex === 0}
                      className="p-2 rounded-full border border-gray-300 hover:bg-white disabled:opacity-30 transition-all text-eco-dark bg-white/50 shadow-sm"
                    >
                      <ArrowLeft className="w-4 h-4" />
                    </button>
                    <span className="font-bold text-sm text-eco-dark w-12 text-center select-none">
                      {currentIdeaIndex + 1} / {Math.max(generatedIdeas.length, 3)}
                    </span>
                    <button 
                      onClick={() => setCurrentIdeaIndex(Math.min(generatedIdeas.length - 1, currentIdeaIndex + 1))}
                      disabled={currentIdeaIndex === generatedIdeas.length - 1}
                      className="p-2 rounded-full border border-gray-300 hover:bg-white disabled:opacity-30 transition-all text-eco-dark bg-white/50 shadow-sm"
                    >
                      <ArrowRight className="w-4 h-4" />
                    </button>
                    <button onClick={() => setStep(1)} className="ml-4 px-4 py-2 bg-gray-200 rounded-lg font-bold text-sm hover:bg-gray-300 transition-colors">Start Over</button>
                  </div>
                </div>
                
                <div className="prose prose-lg max-w-none font-sans bg-white/40 p-6 rounded-2xl border border-white/20 h-[500px] overflow-y-auto scrollbar-hide shadow-inner relative">
                  {generatedIdeas[currentIdeaIndex] ? (
                    <ReactMarkdown
                      components={{
                        h2: ({node, ...props}: any) => <h2 className="text-2xl lg:text-3xl font-serif font-bold text-[#1e3a29] border-b border-black/10 pb-3 mb-6" {...props} />,
                        h3: ({node, ...props}: any) => <h3 className="text-lg lg:text-xl font-bold uppercase tracking-widest text-[#0a100d] mb-4 mt-8" {...props} />,
                        strong: ({node, ...props}: any) => <strong className="font-extrabold text-[#1e3a29]" {...props} />,
                        ul: ({node, ...props}: any) => <ul className="list-disc ml-6 mb-8 space-y-2 opacity-90 text-[1.05rem]" {...props} />,
                        p: ({node, ...props}: any) => <p className="mb-6 leading-relaxed opacity-90 text-[1.1rem]" {...props} />,
                        ol: ({node, ...props}: any) => <ol className="list-decimal marker:font-bold marker:text-[#1e3a29] ml-6 mb-8 space-y-3 opacity-90 text-[1.05rem]" {...props} />,
                      }}
                    >
                      {generatedIdeas[currentIdeaIndex]}
                    </ReactMarkdown>
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <Loader2 className="w-8 h-8 text-eco-primary animate-spin" />
                    </div>
                  )}

                  {/* Progressive loading indicator inside the slide if waiting for more */}
                  {generatedIdeas.length < 3 && currentIdeaIndex === generatedIdeas.length - 1 && (
                    <div className="mt-12 flex items-center justify-center gap-3 text-sm font-bold text-eco-primary animate-pulse bg-white/60 backdrop-blur-md p-4 rounded-xl border border-eco-primary/20 shadow-sm mb-4">
                      <Loader2 className="w-4 h-4 animate-spin" /> Digging deeper for the next idea...
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Right Column: Mini History & Chat Context Container */}
      <motion.div 
        initial={{ opacity: 0, x: 30 }}
        animate={{ opacity: 1, x: 0 }}
        className="w-full md:w-1/3 flex flex-col gap-6"
      >
        <div className="glass-card p-6 h-[800px] flex flex-col">
          <h3 className="font-bold flex items-center gap-2 mb-4 text-eco-dark uppercase tracking-wider text-sm border-b border-gray-200 pb-4">
            <HistoryIcon className="w-4 h-4" /> Recent Scans
          </h3>
          
          <div className="flex-1 overflow-y-auto space-y-3 pr-2 scrollbar-hide">
            {[1,2,3].map((_, i) => (
              <motion.div 
                key={i}
                whileHover={{ scale: 1.02 }}
                className="p-3 rounded-lg bg-white/40 border border-white/20 cursor-pointer hover:border-eco-accent transition-colors flex justify-between items-center group"
              >
                <div>
                  <h4 className="font-bold text-sm truncate w-32">Glass Jar Upcycle</h4>
                  <p className="text-xs text-gray-500">2 mins ago</p>
                </div>
                <div className="flex gap-2">
                  <button className="p-1.5 text-gray-400 hover:text-eco-accent opacity-0 group-hover:opacity-100 transition-opacity"><Edit2 className="w-3.5 h-3.5" /></button>
                  <button className="p-1.5 text-gray-400 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"><Trash2 className="w-3.5 h-3.5" /></button>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </motion.div>

    </div>
  );
};

