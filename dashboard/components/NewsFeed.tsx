"use client";

import React, { useState, useEffect } from 'react';
import styles from './NewsFeed.module.css';

import { getApiUrl } from '@/lib/api';

interface NewsItem {
  id: number;
  external_id: string;
  title: string;
  content: string;
  status: string;
  trace_id: string;
}

interface Props {
  onViewDrafts: (id: number) => void;
}

const NewsFeed = ({ onViewDrafts }: Props) => {
  const [items, setItems] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchItems = async () => {
      try {
        const res = await fetch(getApiUrl('/news-items'));
        if (!res.ok) {
          const text = await res.text();
          console.error(`API Error (${res.status}):`, text);
          return;
        }
        const data = await res.json();
        setItems(data);
      } catch (error) {
        console.error("Failed to fetch news items", error);
      } finally {
        setLoading(false);
      }
    };

    fetchItems();
  }, []);

  const getStatusBadge = (status: string) => {
    const s = status.toUpperCase();
    if (s === 'PROCESSING' || s === 'RECEIVED') return <span className="badge badge-processing">Processing</span>;
    if (s === 'COMPLETED') return <span className="badge badge-completed">Completed</span>;
    if (s === 'FAILED') return <span className="badge badge-failed">Failed</span>;
    return <span className="badge">{status}</span>;
  };

  if (loading) return <div className={styles.loading}>Loading Factory Feed...</div>;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h3>Recent News Ingestion</h3>
        <p>Real-time view of organizational news being processed.</p>
      </div>

      <div className={styles.tableWrapper}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>ID</th>
              <th>Source Title</th>
              <th>Status</th>
              <th>Trace ID</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            {items.map((item) => (
              <tr key={item.id} className={styles.row}>
                <td className={styles.externalId}>{item.external_id}</td>
                <td className={styles.title}>{item.title}</td>
                <td>{getStatusBadge(item.status)}</td>
                <td className={styles.traceId}>{item.trace_id.slice(0, 8)}...</td>
                <td>
                  <button 
                    className="button button-outline"
                    onClick={() => onViewDrafts(item.id)}
                  >
                    View Drafts
                  </button>
                </td>
              </tr>
            ))}
            {items.length === 0 && (
              <tr>
                <td colSpan={5} className={styles.empty}>No news items found. Trigger a webhook to see them here.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default NewsFeed;
