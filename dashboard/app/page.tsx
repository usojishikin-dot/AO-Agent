"use client";

import React, { useState } from 'react';
import NewsFeed from '@/components/NewsFeed';
import ContentStudio from '@/components/ContentStudio';
import IntegrationModal from '@/components/IntegrationModal';
import styles from './page.module.css';

export default function Home() {
  const [selectedItemId, setSelectedItemId] = useState<number | null>(null);
  const [isIntegrationOpen, setIsIntegrationOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefetch = () => {
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div className="scrollable-area">
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Production Dashboard</h1>
          <p className={styles.subtitle}>Manage your enterprise AI content pipeline.</p>
        </div>
        <div className={styles.actions}>
          <button className="button button-outline" onClick={handleRefetch}>Refetch Data</button>
          <button className="button button-primary" onClick={() => setIsIntegrationOpen(true)}>Integration Hub</button>
        </div>
      </header>
      
      <div className={styles.statsGrid}>
        <div className="card">
          <p className={styles.statLabel}>Active News</p>
          <h2 className={styles.statValue}>12</h2>
          <p className={styles.statChange}>+2 from yesterday</p>
        </div>
        <div className="card">
          <p className={styles.statLabel}>Avg. Eval Score</p>
          <h2 className={styles.statValue}>8.4</h2>
          <p className={styles.statChange}>+0.3 from last week</p>
        </div>
        <div className="card">
          <p className={styles.statLabel}>Published Today</p>
          <h2 className={styles.statValue}>4</h2>
          <p className={styles.statChange}>Target: 10</p>
        </div>
      </div>
      
      <NewsFeed key={refreshKey} onViewDrafts={(id) => setSelectedItemId(id)} />

      {selectedItemId && (
        <ContentStudio 
          newsItemId={selectedItemId} 
          onClose={() => setSelectedItemId(null)} 
        />
      )}

      {isIntegrationOpen && (
        <IntegrationModal onClose={() => setIsIntegrationOpen(false)} />
      )}
    </div>
  );
}
