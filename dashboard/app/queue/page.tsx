"use client";

import React, { useState, useEffect } from 'react';
import { getApiUrl } from '@/lib/api';
import { showToast } from '@/lib/toast';
import { CheckCircle, Clock, AlertCircle } from 'lucide-react';
import styles from './page.module.css';

interface ContentVersion {
  id: number;
  news_item_id: number;
  platform: string;
  version_number: number;
  content_text: string;
  status: string;
  evaluation_score?: number;
  evaluation_feedback?: string;
}

export default function QueuePage() {
  const [items, setItems] = useState<ContentVersion[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(getApiUrl('/content-versions?status=GENERATED'))
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

  const handleApprove = async (id: number) => {
    try {
      const res = await fetch(getApiUrl(`/content-versions/${id}/approve`), { method: 'POST' });
      if (res.ok) {
        showToast("Content approved and queued for publishing!");
        setItems(prev => prev.filter(item => item.id !== id));
      } else {
        showToast("Failed to approve content", "error");
      }
    } catch (err) {
      showToast("Error approving content", "error");
    }
  };

  return (
    <div className="scrollable-area">
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Approval Queue</h1>
          <p className={styles.subtitle}>Review generated content before publishing</p>
        </div>
      </header>

      {loading ? (
        <p className={styles.emptyState}>Loading queue...</p>
      ) : items.length === 0 ? (
        <div className={styles.emptyState}>
          <CheckCircle size={48} className={styles.emptyIcon} />
          <p>You're all caught up! No pending items.</p>
        </div>
      ) : (
        <div className={styles.queueGrid}>
          {items.map(item => (
            <div key={item.id} className={`card ${styles.queueCard}`}>
              <div className={styles.cardHeader}>
                <span className={styles.platformBadge}>{item.platform}</span>
                {item.evaluation_score && (
                  <span className={item.evaluation_score > 8 ? styles.scoreHigh : styles.scoreMedium}>
                    Score: {item.evaluation_score}/10
                  </span>
                )}
              </div>
              <p className={styles.contentText}>{item.content_text}</p>
              
              {item.evaluation_feedback && (
                <div className={styles.feedbackBox}>
                  <AlertCircle size={14} />
                  <span>{item.evaluation_feedback}</span>
                </div>
              )}

              <div className={styles.actions}>
                <button className="btn btn-primary" onClick={() => handleApprove(item.id)}>
                  Approve & Publish
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
