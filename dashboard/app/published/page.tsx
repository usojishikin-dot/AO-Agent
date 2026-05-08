"use client";

import React, { useState, useEffect } from 'react';
import { getApiUrl } from '@/lib/api';
import { ExternalLink, CheckCircle } from 'lucide-react';
import styles from '../queue/page.module.css';

interface ContentVersion {
  id: number;
  news_item_id: number;
  platform: string;
  version_number: number;
  content_text: string;
  status: string;
  ayrshare_post_id?: string;
  published_at?: string;
}

export default function PublishedPage() {
  const [items, setItems] = useState<ContentVersion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(getApiUrl('/content-versions?status=PUBLISHED'))
      .then(res => res.json())
      .then(data => {
        setItems(data);
        setLoading(false);
      })
      .catch(err => {
        console.error(err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="scrollable-area">
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Published History</h1>
          <p className={styles.subtitle}>Review content that is live on your social channels</p>
        </div>
      </header>

      {loading ? (
        <p className={styles.emptyState}>Loading history...</p>
      ) : items.length === 0 ? (
        <div className={styles.emptyState}>
          <CheckCircle size={48} className={styles.emptyIcon} />
          <p>No published content found.</p>
        </div>
      ) : (
        <div className={styles.queueGrid}>
          {items.map(item => (
            <div key={item.id} className={`card ${styles.queueCard}`}>
              <div className={styles.cardHeader}>
                <span className={styles.platformBadge}>{item.platform}</span>
                {item.published_at && (
                  <span className={styles.scoreHigh}>
                    {new Date(item.published_at).toLocaleDateString()}
                  </span>
                )}
              </div>
              <p className={styles.contentText}>{item.content_text}</p>
              
              <div className={styles.actions}>
                {item.ayrshare_post_id && (
                  <button className="btn btn-secondary" onClick={() => window.open(`https://app.ayrshare.com`, '_blank')}>
                    <ExternalLink size={14} />
                    View in Ayrshare
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
