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
import { useSession, signOut } from 'next-auth/react';

const Sidebar = () => {
  const [isOpen, setIsOpen] = useState(false);
  const pathname = usePathname();
  const { data: session } = useSession();

  const toggleSidebar = () => {
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
            <Link href="/queue" className={`${styles.navLink} ${pathname === '/queue' ? styles.active : ''}`} onClick={() => setIsOpen(false)}>
              <List size={18} className={styles.icon} />
              Queue
            </Link>
            <Link href="/published" className={`${styles.navLink} ${pathname === '/published' ? styles.active : ''}`} onClick={() => setIsOpen(false)}>
              <CheckCircle size={18} className={styles.icon} />
              Published
            </Link>
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
          {session ? (
            <div className={styles.userProfile} onClick={() => signOut()} style={{ cursor: 'pointer' }}>
              <div className={styles.avatar}>{session.user?.name?.[0] || session.user?.email?.[0]?.toUpperCase() || 'U'}</div>
              <div className={styles.userInfo}>
                <p className={styles.userName}>{session.user?.name || session.user?.email}</p>
                <p className={styles.userRole}>Sign Out</p>
              </div>
            </div>
          ) : (
            <Link href="/login" style={{ textDecoration: 'none' }}>
              <div className={styles.userProfile} style={{ cursor: 'pointer' }}>
                <div className={styles.avatar}>?</div>
                <div className={styles.userInfo}>
                  <p className={styles.userName}>Guest</p>
                  <p className={styles.userRole}>Sign In</p>
                </div>
              </div>
            </Link>
          )}
        </div>
      </aside>
      
      {isOpen && <div className={styles.backdrop} onClick={toggleSidebar} />}
    </>
  );
};

export default Sidebar;
