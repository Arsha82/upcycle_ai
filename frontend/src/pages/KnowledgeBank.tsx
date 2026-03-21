import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Database, UploadCloud, FileText, Server, RefreshCw, Layers } from 'lucide-react';

export const KnowledgeBank: React.FC = () => {
  const [stats, setStats] = useState<{count: number}>({ count: 0 });
  const [isProcessing, setIsProcessing] = useState<string | null>(null);
  const [message, setMessage] = useState<{text: string, type: 'success' | 'error'} | null>(null);

  const fetchStats = async () => {
    try {
      const res = await fetch('http://localhost:8000/api/kb/stats');
      const data = await res.json();
      setStats(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleAction = async (endpoint: string, actionName: string) => {
    setIsProcessing(actionName);
    setMessage(null);
    try {
      const res = await fetch(`http://localhost:8000/api/kb/${endpoint}`, { method: 'POST' });
      const data = await res.json();
      if (res.ok) {
        setMessage({text: data.message || 'Success!', type: 'success'});
        fetchStats();
      } else {
        setMessage({text: data.detail || 'Error occurred', type: 'error'});
      }
    } catch(err: any) {
      setMessage({text: err.message, type: 'error'});
    }
    setIsProcessing(null);
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files?.length) return;
    setIsProcessing('upload');
    setMessage(null);
    try {
      const formData = new FormData();
      Array.from(e.target.files).forEach(f => formData.append('files', f));
      
      const res = await fetch('http://localhost:8000/api/kb/upload', {
        method: 'POST',
        body: formData
      });
      const data = await res.json();
      if (res.ok) {
        setMessage({text: `Successfully processed ${e.target.files.length} file(s).`, type: 'success'});
        fetchStats();
      } else {
        setMessage({text: data.detail || 'Upload failed', type: 'error'});
      }
    } catch(err: any) {
      setMessage({text: err.message, type: 'error'});
    }
    setIsProcessing(null);
  };

  return (
    <div className="dashboard-content tracking-tight">
      <div className="max-w-5xl mx-auto w-full flex flex-col gap-6 pb-12">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="card">
          <h1 className="text-2xl font-bold flex items-center gap-3 text-gray-800 mb-2">
            <Database className="w-8 h-8 text-eco-primary" /> Manage Knowledge Bank
          </h1>
          <p className="text-gray-500 text-sm">Populate your local Vector Database with UPcycling ideas and project instructions!</p>
        </motion.div>

        {message && (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className={`p-4 rounded-xl border font-bold ${message.type === 'error' ? 'bg-red-50 border-red-200 text-red-700' : 'bg-green-50 border-green-200 text-green-800 shadow-sm'}`}>
            {message.text}
          </motion.div>
        )}

        <div className="flex flex-col gap-6">
          {/* Section 1 */}
          <section className="card">
            <div className="card-header">
              <h3 className="font-bold text-lg flex items-center gap-3">
                <span className="bg-gray-100 px-3 py-1 rounded-lg text-gray-500 text-sm border border-black/5">1</span> Ingest Synthetic Dataset
              </h3>
            </div>
            <button 
              disabled={isProcessing !== null}
              onClick={() => handleAction('ingest-csv', 'csv')}
              className="flex items-center gap-3 px-6 py-3 rounded-xl border border-gray-300 bg-white hover:border-eco-primary hover:text-eco-primary transition-colors text-gray-700 font-medium disabled:opacity-50 shadow-sm self-start"
            >
              {isProcessing === 'csv' ? <RefreshCw className="w-5 h-5 animate-spin"/> : <FileText className="w-5 h-5"/>}
              Ingest <code className="bg-gray-100 px-2 py-1 rounded border border-gray-200 text-sm">upcycle_knowledge_llm.csv</code>
            </button>
          </section>

          {/* Section 2 */}
          <section className="card">
            <div className="card-header">
              <h3 className="font-bold text-lg flex items-center gap-3">
                <span className="bg-gray-100 px-3 py-1 rounded-lg text-gray-500 text-sm border border-black/5">2</span> Sync Past History
              </h3>
            </div>
            <button 
              disabled={isProcessing !== null}
              onClick={() => handleAction('sync-history', 'history')}
              className="flex items-center gap-3 px-6 py-3 rounded-xl border border-gray-300 bg-white hover:border-eco-primary hover:text-eco-primary transition-colors text-gray-700 font-medium disabled:opacity-50 shadow-sm self-start"
            >
              {isProcessing === 'history' ? <RefreshCw className="w-5 h-5 animate-spin"/> : <Server className="w-5 h-5"/>}
              Sync <code className="bg-gray-100 px-2 py-1 rounded border border-gray-200 text-sm">upcycle.db</code> History
            </button>
          </section>

          {/* Section 3 */}
          <section className="card relative overflow-hidden">
            <div className="card-header">
              <h3 className="font-bold text-lg flex items-center gap-3">
                <span className="bg-gray-100 px-3 py-1 rounded-lg text-gray-500 text-sm border border-black/5">3</span> Upload Custom Documents
              </h3>
            </div>
            <p className="text-gray-500 mb-4 text-xs font-semibold uppercase tracking-wider">Upload PDF or TXT files</p>
            
            <div className="relative border-2 border-dashed border-gray-300 rounded-2xl p-10 hover:border-eco-primary bg-gray-50 transition-colors flex flex-col items-center justify-center cursor-pointer group" onClick={() => document.getElementById('kbUpload')?.click()}>
              <UploadCloud className="w-10 h-10 text-gray-400 mb-3 group-hover:text-eco-primary transition-colors" />
              <span className="font-medium text-gray-700">Drag and drop files here or Click</span>
              <span className="text-xs text-gray-400 mt-2">Limit 200MB per file • PDF, TXT</span>
              <input id="kbUpload" type="file" multiple accept=".pdf,.txt" className="hidden" onChange={handleFileUpload} />
              {isProcessing === 'upload' && (
                <div className="absolute inset-0 bg-white/80 backdrop-blur-sm rounded-2xl flex flex-col items-center justify-center">
                  <RefreshCw className="w-8 h-8 text-eco-primary animate-spin mb-2" />
                  <span className="font-bold text-eco-primary">Processing Files...</span>
                </div>
              )}
            </div>
          </section>

          {/* Info Box */}
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="bg-[#eaf1ec] border border-[#a3c2b0] rounded-xl p-4 flex items-center gap-4 text-[#1e3a29] shadow-inner">
            <Layers className="w-6 h-6" />
            <span className="font-medium text-sm">Knowledge Bank Size: <strong>{stats.count}</strong> total chunks/documents stored.</span>
          </motion.div>

        </div>
      </div>
    </div>
  );
};
