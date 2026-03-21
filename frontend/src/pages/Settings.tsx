import React from 'react';
import { motion } from 'framer-motion';

export const Settings: React.FC = () => {
  return (
    <div className="dashboard-content">
      <motion.div 
        className="card"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="card-header">
          <h3>System Settings</h3>
        </div>
        <div className="p-4 text-gray-500 text-sm h-64 flex items-center justify-center">
          Configuration options for Local Inference Engine
          <br/>
          (Coming Soon)
        </div>
      </motion.div>
    </div>
  );
};
