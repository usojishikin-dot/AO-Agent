"use client";

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import styles from './Sidebar.module.css';
import { 
  Home, 
  List, 
  CheckCircle, 
  BarChart3, 
  Zap, 
  Menu, 
  X,
  Settings
} from 'lucide-react';
import { showToast } from '@/lib/toast';

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();

  const toggleSidebar = (e?: React.MouseEvent | React.HTMLAttributes<HTMLButtonElement>) => {
    // We remove preventDefault to ensure the event flows naturally on mobile
    console.log("Toggle Sidebar Triggered");
    setIsOpen(prev => !prev);
  };

  const handleComingSoon = (e: React.MouseEvent, feature: string) => {
    e.preventDefault();
    setIsOpen(false);
    showToast(`Coming Soon: ${feature} unlocks in Phase 2!`);
  };

  return (
    <>
      <button 
        type="button"
        className={styles.mobileToggle} 
        onClick={() => toggleSidebar()}
        aria-label={isOpen ? "Close Menu" : "Open Menu"}
      >
        {isOpen ? <X size={24} /> : <Zap size={24} fill="currentColor" />}
      </button>

      <aside className={`${styles.sidebar} ${isOpen ? styles.open : ''}`}>
        <div className={styles.logo}>
          <div className={styles.logoIcon}>CF</div>
          <span className={styles.logoText}>Content Factory</span>
        </div>
        
        <nav className={styles.nav}>
          <div className={styles.navSection}>
            <p className={styles.sectionTitle}>Main</p>
            <Link href="/" className={`${styles.navLink} ${pathname === '/' ? styles.active : ''}`} onClick={() => setIsOpen(false)}>
              <Home size={18} className={styles.icon} />
              Dashboard
            </Link>
            <a href="#" className={styles.navLink} onClick={(e) => handleComingSoon(e, 'Queue')}>
              <List size={18} className={styles.icon} />
              Queue
            </a>
            <a href="#" className={styles.navLink} onClick={(e) => handleComingSoon(e, 'Published')}>
              <CheckCircle size={18} className={styles.icon} />
              Published
            </a>
          </div>
          
          <div className={styles.navSection}>
            <p className={styles.sectionTitle}>Analytics</p>
            <Link href="/analytics" className={`${styles.navLink} ${pathname === '/analytics' ? styles.active : ''}`} onClick={() => setIsOpen(false)}>
              <BarChart3 size={18} className={styles.icon} />
              Performance
            </Link>
            <Link href="/analytics" className={`${styles.navLink} ${pathname === '/analytics' ? styles.active : ''}`} onClick={() => setIsOpen(false)}>
              <Zap size={18} className={styles.icon} />
              AI Insights
            </Link>
          </div>

          <div className={styles.navSection}>
            <p className={styles.sectionTitle}>System</p>
            <a href="#" className={styles.navLink} onClick={(e) => handleComingSoon(e, 'Settings')}>
              <Settings size={18} className={styles.icon} />
              Settings
            </a>
          </div>
        </nav>
        
        <div className={styles.footer}>
          <div className={styles.userProfile}>
            <div className={styles.avatar}>M</div>
            <div className={styles.userInfo}>
              <p className={styles.userName}>Memmun</p>
              <p className={styles.userRole}>Admin</p>
            </div>
          </div>
        </div>
      </aside>
      
      {isOpen && <div className={styles.backdrop} onClick={toggleSidebar} />}
    </>
  );
};

export default Sidebar;
