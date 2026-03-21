import React, { useEffect, useState } from 'react';
import { motion } from 'framer-motion';
import { Search, Filter, Calendar, Zap, RefreshCw, ArrowRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

}

export const Explore: React.FC<ExploreProps> = ({ searchQuery = '' }) => {
  const navigate = useNavigate();

  // Mock Data
  const [scanHistory] = useState([
    { id: '1001', material: 'Glass Bottle', project: 'Terrarium', type: 'Glass', time: '10:45 AM' },
    { id: '1002', material: 'Cardboard Box', project: 'Storage Bin', type: 'Paper', time: 'Yesterday' },
    { id: '1003', material: 'Plastic Crate', project: 'Planter', type: 'Plastic', time: '2 Days Ago' },
    { id: '1004', material: 'Denim Jeans', project: 'Tote Bag', type: 'Fabric', time: '3 Days Ago' },
  ]);

  const totalScans = scanHistory.length;
  const donutData = [
    { name: 'Glass', value: 1, fill: '#3b82f6' },
    { name: 'Paper', value: 1, fill: '#10b981' },
    { name: 'Plastic', value: 1, fill: '#f59e0b' },
    { name: 'Fabric', value: 1, fill: '#8b5cf6' }
  ];

  const lineData = [
    { day: 'Mon', count: 2 },
    { day: 'Tue', count: 5 },
    { day: 'Wed', count: 3 },
    { day: 'Thu', count: 8 },
    { day: 'Fri', count: 4 },
  ];

  return (
    <div className="dashboard-content">
      <div className="metrics-grid">
        
        {/* Card 1: Primary Dark Stats */}
        <motion.div 
          className="card primary-dark"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          <div className="card-header">
            <h3>Total Upcycles</h3>
            <div className="dropdown-text text-white/70">Current Session</div>
          </div>
          <div className="stats-row">
            <div className="stat-item">
              <span className="stat-number">{totalScans}</span>
              <div className="stat-info">
                <span className="stat-label">Materials Scanned</span>
              </div>
            </div>
            <div className="stat-item">
              <span className="stat-number text-[#34d399]">12</span>
              <div className="stat-info">
                <span className="stat-label text-white/80">Ideas Generated</span>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Card 2: Donut Chart */}
        <motion.div 
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.1 }}
        >
          <div className="card-header">
            <h3>Material Breakdown</h3>
          </div>
          <div style={{ height: '140px', position: 'relative' }}>
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={donutData}
                  cx="50%"
                  cy="50%"
                  innerRadius={40}
                  outerRadius={60}
                  dataKey="value"
                  stroke="none"
                  animationDuration={1500}
                >
                  {donutData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.fill} />
                  ))}
                </Pie>
              </PieChart>
            </ResponsiveContainer>
            <div style={{ position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', textAlign: 'center' }}>
              <div style={{ fontWeight: 600, fontSize: '0.9rem' }}>{totalScans}</div>
              <div style={{ fontSize: '0.65rem', color: '#6b7280' }}>total</div>
            </div>
          </div>
        </motion.div>

        {/* Card 3: Line Chart */}
        <motion.div 
          className="card"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.2 }}
        >
          <div className="card-header">
            <h3>Generation Volume</h3>
            <div className="dropdown-text">Last 5 Days</div>
          </div>
          
          <div style={{ height: '160px', width: '100%', marginTop: 'auto' }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={lineData} margin={{ top: 5, right: 10, left: 10, bottom: 0 }}>
                <RechartsTooltip formatter={(value) => new Intl.NumberFormat().format(Number(value)) + " ideas"} labelStyle={{ color: '#1f2937' }} />
                <Line type="monotone" name="Ideas Generated" dataKey="count" stroke="#10b981" strokeWidth={3} dot={{r: 4, fill: '#10b981', strokeWidth: 2, stroke: 'white'}} animationDuration={2000}/>
                <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 10, fill: '#9ca3af' }} dy={10} />
                <YAxis hide domain={['dataMin - 1', 'dataMax + 2']} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </motion.div>

        {/* Card 4: Contacts / Recent History */}
        <motion.div 
          className="card" style={{ gridRow: 'span 2', overflowY: 'auto' }}
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.4, delay: 0.3 }}
        >
          <div className="card-header">
            <h3>{searchQuery ? 'Search Results' : 'Recent Scans'}</h3>
          </div>
          <div style={{ display:'flex', flexDirection:'column', gap:'1.5rem', marginTop:'1rem' }}>
            {(() => {
               const filteredScans = scanHistory.filter(scan => {
                 if (!searchQuery) return true;
                 const q = searchQuery.toLowerCase();
                 return (
                   scan.project.toLowerCase().includes(q) ||
                   scan.material.toLowerCase().includes(q) ||
                   scan.type.toLowerCase().includes(q)
                 );
               });

               if (filteredScans.length === 0) {
                 return (
                   <div style={{ color: '#9ca3af', fontSize: '0.85rem', textAlign: 'center', marginTop: '2rem' }}>
                     {searchQuery ? 'No scans match your search.' : ['No active scans.', <br key="br"/>, 'Upload a material to see history here.']}
                   </div>
                 );
               }

               return filteredScans.map((scan) => (
                <div key={scan.id} style={{ display:'flex', alignItems:'center', gap:'1rem' }}>
                  <div style={{ 
                      width:'40px', height:'40px', borderRadius:'10px', 
                      background: '#ecfdf5',
                      color: '#10b981',
                      display: 'flex', alignItems: 'center', justifyContent: 'center'
                  }}>
                    <Lightbulb size={20}/>
                  </div>
                  <div style={{ flex:1 }}>
                    <div style={{ fontSize:'0.9rem', fontWeight:600 }}>
                       {scan.project}
                    </div>
                    <div style={{ fontSize:'0.75rem', color: '#6b7280' }}>
                       {scan.time} • {scan.material}
                    </div>
                  </div>
                </div>
              ))
            })()}
          </div>
        </motion.div>

        {/* Bottom Wide Card: Workflow Action */}
        <motion.div 
          className="workflow-bottom-card" style={{ gridColumn: 'span 3' }}
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4, delay: 0.4 }}
        >
           <div className="card-header" style={{ marginBottom: 0 }}>
              <h3>Quick Actions</h3>
           </div>
           
           <div className="flex flex-col gap-4 mt-6">
              <div className="flex items-center justify-between p-4 bg-gray-50 rounded-2xl">
                 <div className="w-10 h-10 rounded-full bg-emerald-100 text-[#10b981] flex items-center justify-center"><ScanLine size={20} /></div>
                 <div className="flex-1 ml-6">
                    <h4 className="font-semibold text-[0.95rem]">Analyze New Waste Material</h4>
                    <p className="text-sm text-gray-500">Uses Local Ollama Vision Models</p>
                 </div>
                 <button className="px-5 py-2 rounded-full text-sm font-semibold bg-white border border-[#10b981] text-[#10b981] hover:bg-emerald-50 transition-colors cursor-pointer" onClick={() => navigate('/scanner')}>Launch Scanner</button>
              </div>
           </div>
        </motion.div>

      </div>
    </div>
  );
};
