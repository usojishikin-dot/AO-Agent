"use client";

import React, { useState, useEffect } from 'react';
import styles from './Toast.module.css';
import { Info } from 'lucide-react';

const Toast = () => {
  const [message, setMessage] = useState('');
  const [visible, setVisible] = useState(false);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    
    const handleShow = (e: any) => {
      setMessage(e.detail.message);
      setVisible(true);
      
      clearTimeout(timeout);
      timeout = setTimeout(() => setVisible(false), 3000);
    };

    window.addEventListener('show-toast', handleShow);
    return () => {
      window.removeEventListener('show-toast', handleShow);
      clearTimeout(timeout);
    };
  }, []);

  if (!visible) return null;

  return (
    <div className={styles.toast}>
      <Info size={18} className={styles.icon} />
      <span>{message}</span>
    </div>
  );
};

export default Toast;
