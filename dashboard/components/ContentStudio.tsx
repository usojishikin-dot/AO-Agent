"use client";

import React, { useState, useEffect } from 'react';
import styles from './ContentStudio.module.css';

import { getApiUrl } from '@/lib/api';

import { showToast } from '@/lib/toast';

interface ContentVersion {
  id: number;
  platform: string;
  version_number: number;
  content_text: string;
  status: string;
  evaluation_score: number | null;
  brand_score: number | null;
  human_likeness_score: number | null;
  platform_compliance_score: number | null;
  evaluation_feedback: string | null;
  approved_by_human: boolean;
}

interface NewsItem {
  id: number;
  title: string;
  content: string;
  master_outline: string | null;
  status: string;
}

interface Props {
  newsItemId: number | null;
  onClose: () => void;
}

const ContentStudio = ({ newsItemId, onClose }: Props) => {
  const [newsItem, setNewsItem] = useState<NewsItem | null>(null);
  const [versions, setVersions] = useState<ContentVersion[]>([]);
  const [activeTab, setActiveTab] = useState('x');
  const [loading, setLoading] = useState(true);
  const [publishing, setPublishing] = useState<number | null>(null);

  useEffect(() => {
    if (!newsItemId) return;

    const fetchData = async () => {
      setLoading(true);
      try {
        const [newsRes, versionsRes] = await Promise.all([
          fetch(getApiUrl(`/news-items/${newsItemId}`)),
          fetch(getApiUrl(`/news-items/${newsItemId}/versions`))
        ]);
        
        const newsData = await newsRes.json();
        const versionsData = await versionsRes.json();
        
        setNewsItem(newsData);
        setVersions(versionsData);
        
        // Set first available platform as active
        if (versionsData.length > 0) {
          setActiveTab(versionsData[0].platform);
        }
      } catch (error) {
        console.error("Failed to fetch studio data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [newsItemId]);

  const handleApprove = async (cvId: number) => {
    setPublishing(cvId);
    try {
      const res = await fetch(getApiUrl(`/content-versions/${cvId}/approve`), {
        method: 'POST'
      });
      if (res.ok) {
        // Update local state
        setVersions(versions.map(v => v.id === cvId ? { ...v, approved_by_human: true } : v));
      }
    } catch (error) {
      console.error("Approval failed", error);
    } finally {
      setPublishing(null);
    }
  };

  if (!newsItemId) return null;
  if (loading) return <div className={styles.overlay}><div className={styles.loading}>Opening Studio...</div></div>;
  if (!newsItem) return null;

  const currentVersion = versions.find(v => v.platform === activeTab);

  return (
    <div className={styles.overlay}>
      <div className={styles.studio}>
        <header className={styles.header}>
          <div>
            <span className="badge badge-completed">Studio Mode</span>
            <h2>{newsItem.title}</h2>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </header>

        <div className={styles.body}>
          <div className={styles.leftPanel}>
            <section className={styles.section}>
              <h4>Source Content</h4>
              <div className={styles.contentBox}>{newsItem.content}</div>
            </section>
            
            <section className={styles.section}>
              <h4>Master Concept Outline (Gemini Flash)</h4>
              <div className={`${styles.contentBox} ${styles.outline}`}>
                {newsItem.master_outline || "Outline not generated yet."}
              </div>
            </section>
          </div>

          <div className={styles.rightPanel}>
            <div className={styles.tabs}>
              {['x', 'linkedin', 'facebook'].map(p => (
                <button 
                  key={p}
                  className={`${styles.tab} ${activeTab === p ? styles.activeTab : ''}`}
                  onClick={() => setActiveTab(p)}
                >
                  {p.toUpperCase()}
                </button>
              ))}
            </div>

            <div className={styles.draftContainer}>
              {currentVersion ? (
                <>
                  <div className={styles.draftHeader}>
                    <div className={styles.scores}>
                      <ScoreBadge label="Brand" score={currentVersion.brand_score} />
                      <ScoreBadge label="Human" score={currentVersion.human_likeness_score} />
                      <ScoreBadge label="Platform" score={currentVersion.platform_compliance_score} />
                    </div>
                    <div className={styles.overallScore}>
                      <span>Overall Score</span>
                      <strong>{(currentVersion.evaluation_score || 0) * 10}</strong>
                    </div>
                  </div>

                  <div className={styles.draftText}>
                    {currentVersion.content_text}
                  </div>

                  {currentVersion.evaluation_feedback && (
                    <div className={styles.feedback}>
                      <strong>Editor Feedback:</strong>
                      <p>{currentVersion.evaluation_feedback}</p>
                    </div>
                  )}

                  <div className={styles.actions}>
                    <button 
                      className="button button-outline"
                      onClick={() => showToast('Coming Soon: Manual Draft Editing unlocks in Phase 2!')}
                    >
                      Edit Draft
                    </button>
                    <button 
                      className={`button button-primary ${styles.approveBtn}`}
                      disabled={currentVersion.approved_by_human || publishing === currentVersion.id}
                      onClick={() => handleApprove(currentVersion.id)}
                    >
                      {currentVersion.approved_by_human ? '✓ Approved' : publishing === currentVersion.id ? 'Publishing...' : 'Approve & Publish'}
                    </button>
                  </div>
                </>
              ) : (
                <div className={styles.emptyDraft}>No draft generated for this platform.</div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const ScoreBadge = ({ label, score }: { label: string, score: number | null }) => {
  const s = (score || 0) * 10;
  const getColor = () => {
    if (s >= 8) return '#10b981';
    if (s >= 6) return '#f59e0b';
    return '#ef4444';
  };

  return (
    <div className={styles.scoreBadge}>
      <span className={styles.scoreLabel}>{label}</span>
      <span className={styles.scoreValue} style={{ color: getColor() }}>{s.toFixed(1)}</span>
    </div>
  );
};

export default ContentStudio;
