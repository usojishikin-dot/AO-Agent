"use client";

import React from 'react';
import styles from './page.module.css';
import { TrendingUp, Users, Target, Zap, Activity } from 'lucide-react';

export default function AnalyticsPage() {
  return (
    <div className="scrollable-area">
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Analytics & AI Insights</h1>
          <p className={styles.subtitle}>Performance Learning Layer (Ayrshare Feedback Loop)</p>
        </div>
      </header>
      
      <div className={styles.statsGrid}>
        <div className="card">
          <div className={styles.statIconWrapper}><Users size={20} className={styles.statIcon} /></div>
          <p className={styles.statLabel}>Total Reach (30d)</p>
          <h2 className={styles.statValue}>142.5K</h2>
          <p className={`${styles.statChange} ${styles.positive}`}>+14.2% from last period</p>
        </div>
        <div className="card">
          <div className={styles.statIconWrapper}><Activity size={20} className={styles.statIcon} /></div>
          <p className={styles.statLabel}>Avg. Engagement Rate</p>
          <h2 className={styles.statValue}>4.8%</h2>
          <p className={`${styles.statChange} ${styles.positive}`}>+0.5% from last period</p>
        </div>
        <div className="card">
          <div className={styles.statIconWrapper}><Target size={20} className={styles.statIcon} /></div>
          <p className={styles.statLabel}>Best Platform</p>
          <h2 className={styles.statValue}>LinkedIn</h2>
          <p className={styles.statChange}>Drives 65% of all traffic</p>
        </div>
      </div>

      <div className={styles.dashboardBody}>
        <div className={styles.mainChart}>
          <div className={styles.cardHeader}>
            <h3>Engagement by Platform</h3>
            <span className={styles.badge}>Live Data</span>
          </div>
          
          <div className={styles.chartContainer}>
            <div className={styles.chartBar}>
              <div className={styles.barLabel}>LinkedIn</div>
              <div className={styles.barTrack}>
                <div className={styles.barFill} style={{ width: '85%', backgroundColor: '#0a66c2' }}></div>
              </div>
              <div className={styles.barValue}>85%</div>
            </div>
            
            <div className={styles.chartBar}>
              <div className={styles.barLabel}>X (Twitter)</div>
              <div className={styles.barTrack}>
                <div className={styles.barFill} style={{ width: '62%', backgroundColor: '#1da1f2' }}></div>
              </div>
              <div className={styles.barValue}>62%</div>
            </div>
            
            <div className={styles.chartBar}>
              <div className={styles.barLabel}>Facebook</div>
              <div className={styles.barTrack}>
                <div className={styles.barFill} style={{ width: '30%', backgroundColor: '#1877f2' }}></div>
              </div>
              <div className={styles.barValue}>30%</div>
            </div>
          </div>
        </div>

        <div className={styles.aiInsights}>
          <div className={styles.cardHeader}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Zap size={20} color="var(--primary)" />
              <h3>AI Learning Engine</h3>
            </div>
          </div>
          
          <div className={styles.insightsList}>
            <div className={styles.insightCard}>
              <div className={styles.insightTag}>Llama 3.3 Fine-tuning</div>
              <h4>Bullet points increase engagement</h4>
              <p>Analysis shows that LinkedIn posts utilizing formatted bullet points receive <strong>40% higher engagement</strong>. The generation prompt has been automatically adjusted to prioritize this format for future Web3 topics.</p>
            </div>
            
            <div className={styles.insightCard}>
              <div className={styles.insightTag}>Tone Adjustment</div>
              <h4>"Contrarian" tone performs best on X</h4>
              <p>Posts challenging common narratives on X have a <strong>2.5x higher retweet rate</strong>. The Voice Vault parameters for X have been updated to increase the contrarian weighting by 15%.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
