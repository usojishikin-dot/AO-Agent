"use client";

import React, { useState, useEffect } from 'react';
import { getApiUrl } from '@/lib/api';
import { 
  ExternalLink, 
  Search, 
  Calendar, 
  LayoutGrid, 
  Archive,
  Image as ImageIcon
} from 'lucide-react';
import styles from './page.module.css';

interface ContentVersion {
  id: number;
  news_item_id: number;
  platform: string;
  version_number: number;
  content_text: string;
  status: string;
  ayrshare_post_id?: string;
  published_at?: string;
  evaluation_score?: number;
  news_item_title?: string;
  news_item_image?: string;
}

interface GroupedContent {
  news_item_id: number;
  title: string;
  image: string;
  variants: ContentVersion[];
}

export default function PublishedPage() {
  const [items, setItems] = useState<ContentVersion[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');

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

  // Grouping logic: Group versions by news_item_id
  const groupItems = (rawItems: ContentVersion[]): GroupedContent[] => {
    const groups: { [key: number]: GroupedContent } = {};
    
    rawItems.forEach(item => {
      if (!groups[item.news_item_id]) {
        groups[item.news_item_id] = {
          news_item_id: item.news_item_id,
          title: item.news_item_title || 'Untitled Campaign',
          image: item.news_item_image || '',
          variants: []
        };
      }
      groups[item.news_item_id].variants.push(item);
    });

    return Object.values(groups).sort((a, b) => {
      // Sort by the latest published_at in each group
      const latestA = Math.max(...a.variants.map(v => new Date(v.published_at || 0).getTime()));
      const latestB = Math.max(...b.variants.map(v => new Date(v.published_at || 0).getTime()));
      return latestB - latestA;
    });
  };

  const filteredItems = items.filter(item => 
    item.content_text.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (item.news_item_title && item.news_item_title.toLowerCase().includes(searchTerm.toLowerCase())) ||
    item.platform.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const groupedData = groupItems(filteredItems);

  return (
    <div className="scrollable-area">
      <header className={styles.header}>
        <div>
          <h1 className={styles.title}>Content Archive</h1>
          <p className={styles.subtitle}>Historical record of your organization's digital impact</p>
        </div>
        
        <div className={styles.controls}>
          <div style={{ position: 'relative' }}>
            <Search 
              size={16} 
              style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-secondary)' }} 
            />
            <input 
              type="text" 
              placeholder="Search history..." 
              className={styles.search}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
          </div>
        </div>
      </header>

      {loading ? (
        <div className={styles.emptyState}>
          <p>Loading your content history...</p>
        </div>
      ) : groupedData.length === 0 ? (
        <div className={styles.emptyState}>
          <Archive size={48} className={styles.emptyIcon} />
          <p>{searchTerm ? 'No matches found for your search.' : 'No published content yet. Approved posts will appear here.'}</p>
        </div>
      ) : (
        <div className={styles.archiveList}>
          {groupedData.map(group => (
            <section key={group.news_item_id} className={styles.group}>
              <div className={styles.groupHeader}>
                {group.image ? (
                  <img src={group.image} alt={group.title} className={styles.newsImage} />
                ) : (
                  <div className={styles.newsImage} style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <ImageIcon size={20} color="var(--text-secondary)" />
                  </div>
                )}
                <div className={styles.newsInfo}>
                  <h2 className={styles.newsTitle}>{group.title}</h2>
                  <div className={styles.newsMeta}>
                    <LayoutGrid size={12} style={{ display: 'inline', marginRight: '4px' }} />
                    {group.variants.length} Platforms • {new Date(group.variants[0].published_at || '').toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })}
                  </div>
                </div>
              </div>
              
              <div className={styles.variantsGrid}>
                {group.variants.map(variant => (
                  <div key={variant.id} className={styles.variantCard}>
                    <div className={styles.variantMeta}>
                      <span className={styles.platformTag}>{variant.platform.replace('_', ' ')}</span>
                      <span className={styles.dateTag}>
                        <Calendar size={10} style={{ display: 'inline', marginRight: '4px' }} />
                        {new Date(variant.published_at || '').toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <p className={styles.contentText}>{variant.content_text}</p>
                    <div className={styles.actions}>
                      <div className={styles.score}>
                        {variant.evaluation_score ? `AI Score: ${(variant.evaluation_score * 100).toFixed(0)}%` : 'Published'}
                      </div>
                      {variant.ayrshare_post_id && (
                        <button 
                          className={styles.linkBtn}
                          onClick={() => window.open(`https://app.ayrshare.com`, '_blank')}
                        >
                          <ExternalLink size={12} />
                          Ayrshare
                        </button>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
