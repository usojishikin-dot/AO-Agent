"use client";

import React, { useState, useEffect } from 'react';
import styles from './IntegrationModal.module.css';
import { getApiUrl } from '@/lib/api';
import { showToast } from '@/lib/toast';
import { Copy, CheckCircle, Key, Link as LinkIcon, Info } from 'lucide-react';

interface Props {
  onClose: () => void;
}

const IntegrationModal = ({ onClose }: Props) => {
  const [activeTab, setActiveTab] = useState<'website' | 'social'>('website');
  const [config, setConfig] = useState({ webhook_url: '', token: '' });
  const [copied, setCopied] = useState(false);
  const [connectedSocials, setConnectedSocials] = useState<Record<string, boolean>>({});
  const [codeLanguage, setCodeLanguage] = useState<'javascript' | 'python' | 'php' | 'curl'>('javascript');

  useEffect(() => {
    fetch(getApiUrl('/integration-config'))
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(err => console.error("Failed to load config", err));
  }, []);

  const getCodeSnippet = () => {
    const url = `https://[YOUR-BACKEND]${config.webhook_url || '/news-trigger'}`;
    const token = config.token || 'YOUR_TOKEN_HERE';
    
    switch(codeLanguage) {
      case 'javascript':
        return `// Send data to Content Factory Webhook
const payload = {
  external_id: "unique-post-123",
  title: "New Post Title",
  content: "Full post text...",
};

fetch("${url}", {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
    "Authorization": "Bearer ${token}"
  },
  body: JSON.stringify(payload)
});`;
      case 'python':
        return `import requests

url = "${url}"
headers = {
    "Authorization": "Bearer ${token}",
    "Content-Type": "application/json"
}
payload = {
    "external_id": "unique-post-123",
    "title": "New Post Title",
    "content": "Full post text...",
}

response = requests.post(url, json=payload, headers=headers)`;
      case 'php':
        return `<?php
$url = "${url}";
$data = array(
    "external_id" => "unique-post-123",
    "title" => "New Post Title",
    "content" => "Full post text..."
);

$ch = curl_init($url);
curl_setopt($ch, CURLOPT_POSTFIELDS, json_encode($data));
curl_setopt($ch, CURLOPT_HTTPHEADER, array(
    "Authorization: Bearer ${token}",
    "Content-Type: application/json"
));
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
$result = curl_exec($ch);
curl_close($ch);
?>`;
      case 'curl':
        return `curl -X POST "${url}" \\
     -H "Authorization: Bearer ${token}" \\
     -H "Content-Type: application/json" \\
     -d '{
           "external_id": "unique-post-123",
           "title": "New Post Title",
           "content": "Full post text..."
         }'`;
    }
  };

  const handleCopy = () => {
    navigator.clipboard.writeText(getCodeSnippet());
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
    showToast("Code snippet copied to clipboard");
  };

  const handleConnectSocial = (platform: string) => {
    // Simulate OAuth popup delay for prototype
    showToast(`Connecting to ${platform}...`);
    setTimeout(() => {
      setConnectedSocials(prev => ({ ...prev, [platform]: true }));
      showToast(`${platform} successfully connected!`);
    }, 1500);
  };

  return (
    <div className={styles.overlay}>
      <div className={styles.modal}>
        <header className={styles.header}>
          <div>
            <h2>Integration Hub</h2>
            <p className={styles.subtitle}>Connect your website and external social accounts</p>
          </div>
          <button className={styles.closeBtn} onClick={onClose}>✕</button>
        </header>

        <div className={styles.tabs}>
          <button 
            className={`${styles.tab} ${activeTab === 'website' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('website')}
          >
            Website Webhook
          </button>
          <button 
            className={`${styles.tab} ${activeTab === 'social' ? styles.activeTab : ''}`}
            onClick={() => setActiveTab('social')}
          >
            Social Accounts
          </button>
        </div>

        <div className={styles.body}>
          {activeTab === 'website' ? (
            <div className={styles.tabContent}>
              <div className={styles.infoAlert}>
                <Info size={16} />
                <span>Send a POST request to this endpoint whenever a new article is published.</span>
              </div>
              
              <div className={styles.configItem}>
                <label>Webhook Endpoint URL</label>
                <div className={styles.inputGroup}>
                  <LinkIcon size={16} className={styles.inputIcon} />
                  <input type="text" readOnly value={`https://[YOUR-BACKEND]${config.webhook_url || '/news-trigger'}`} />
                </div>
              </div>

              <div className={styles.configItem}>
                <label>Secret Bearer Token</label>
                <div className={styles.inputGroup}>
                  <Key size={16} className={styles.inputIcon} />
                  <input type="text" readOnly value={config.token || '••••••••••••'} />
                </div>
              </div>

              <div className={styles.codeBlockContainer}>
                <div className={styles.codeHeader}>
                  <div className={styles.langSelector}>
                    {(['javascript', 'python', 'php', 'curl'] as const).map(lang => (
                      <button
                        key={lang}
                        className={`${styles.langBtn} ${codeLanguage === lang ? styles.activeLang : ''}`}
                        onClick={() => setCodeLanguage(lang)}
                      >
                        {lang === 'javascript' ? 'Node.js' : lang.toUpperCase()}
                      </button>
                    ))}
                  </div>
                  <button className={styles.copyBtn} onClick={handleCopy}>
                    {copied ? <CheckCircle size={14} /> : <Copy size={14} />}
                    {copied ? 'Copied' : 'Copy Code'}
                  </button>
                </div>
                <pre className={styles.codeBlock}>
                  <code>
{getCodeSnippet()}
                  </code>
                </pre>
              </div>
            </div>
          ) : (
            <div className={styles.tabContent}>
              <p className={styles.instructionText}>Link your organization's social media profiles below to enable direct publishing.</p>
              
              <div className={styles.socialGrid}>
                {['X (Twitter)', 'LinkedIn', 'Facebook'].map(platform => {
                  const isConnected = connectedSocials[platform];
                  return (
                    <div key={platform} className={styles.socialCard}>
                      <div className={styles.socialInfo}>
                        <div className={styles.socialIconPlaceholder}>{platform[0]}</div>
                        <div>
                          <h4>{platform}</h4>
                          <p className={styles.statusText} style={{ color: isConnected ? 'var(--status-completed)' : 'var(--muted-foreground)' }}>
                            {isConnected ? 'Connected' : 'Not linked'}
                          </p>
                        </div>
                      </div>
                      <button 
                        className={`button ${isConnected ? 'button-outline' : 'button-primary'}`}
                        onClick={() => handleConnectSocial(platform)}
                        disabled={isConnected}
                      >
                        {isConnected ? 'Manage' : 'Connect'}
                      </button>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default IntegrationModal;
