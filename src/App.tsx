import { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Toaster, toast } from 'react-hot-toast';
import { 
  Search, Loader2, TrendingUp, FileText, Zap, Upload, Sparkles, BarChart3, 
  XCircle, Command, Download, Share2, Copy, Filter, Settings
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import axios from 'axios';
import FileUpload from './components/FileUpload';
import CommandPalette from './components/CommandPalette';
import AnalyticsDashboard from './components/AnalyticsDashboard';
import QueryTemplates from './components/QueryTemplates';
import SmartSuggestions from './components/SmartSuggestions';
import ComparisonView from './components/ComparisonView';
import QuickInsights from './components/QuickInsights';
import './App.css';
import './styles/clean.css';

const API_BASE_URL = 'http://localhost:8000';

interface AnalyzeResponse {
  query: string;
  companies_found: string[];
  file_paths: string[];
  analysis: string;
  metadata: {
    total_files: number;
    total_content_size: number;
    companies: Array<{
      ticker: string;
      file_path: string;
      content_length: number;
      metadata: any;
    }>;
  };
}

interface QueryHistory {
  id: string;
  query: string;
  timestamp: Date;
  companies: string[];
  tokens?: number;
}

function App() {
  const [activeTab, setActiveTab] = useState<'analyze' | 'upload'>('analyze');
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalyzeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<QueryHistory[]>([]);
  const [totalTokens, setTotalTokens] = useState(0);
  const [commandPaletteOpen, setCommandPaletteOpen] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [showTemplates, setShowTemplates] = useState(true);
  const [showComparison, setShowComparison] = useState(false);
  const [comparisonCompanies, setComparisonCompanies] = useState<string[]>([]);

  // Load history from localStorage
  useEffect(() => {
    const savedHistory = localStorage.getItem('queryHistory');
    if (savedHistory) {
      setHistory(JSON.parse(savedHistory));
    }
    const savedTokens = localStorage.getItem('totalTokens');
    if (savedTokens) {
      setTotalTokens(parseInt(savedTokens, 10));
    }
  }, []);

  // Save history to localStorage
  useEffect(() => {
    if (history.length > 0) {
      localStorage.setItem('queryHistory', JSON.stringify(history));
    }
  }, [history]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setCommandPaletteOpen(true);
      }
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        if (query.trim() && !loading) {
          handleAnalyze();
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [query, loading]);

  const estimateTokens = (text: string): number => {
    return Math.ceil(text.length / 4);
  };

  const formatCost = (tokens: number): string => {
    const inputCost = (tokens * 0.8 * 0.075) / 1000000;
    const outputCost = (tokens * 0.2 * 0.30) / 1000000;
    const totalCost = inputCost + outputCost;
    return totalCost < 0.01 ? '< $0.01' : `$${totalCost.toFixed(4)}`;
  };

  const formatBytes = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
  };

  const handleAnalyze = async () => {
    if (!query.trim()) {
      toast.error('Please enter a query');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await axios.post<AnalyzeResponse>(
        `${API_BASE_URL}/analyze`,
        {
          query: query.trim(),
          max_companies: 5,
        }
      );

      setResult(response.data);
      toast.success('Analysis complete!');

      // Calculate tokens
      const inputTokens = estimateTokens(
        response.data.metadata.total_content_size.toString()
      );
      const outputTokens = estimateTokens(response.data.analysis);
      const queryTokens = estimateTokens(query);
      const totalQueryTokens = inputTokens + outputTokens + queryTokens;

      setTotalTokens((prev) => {
        const newTotal = prev + totalQueryTokens;
        localStorage.setItem('totalTokens', newTotal.toString());
        return newTotal;
      });

      // Add to history
      const newHistoryItem: QueryHistory = {
        id: Date.now().toString(),
        query: query.trim(),
        timestamp: new Date(),
        companies: response.data.companies_found,
        tokens: totalQueryTokens,
      };

      setHistory((prev) => [newHistoryItem, ...prev.slice(0, 9)]);
    } catch (err: any) {
      const errorMsg = err.response?.data?.detail || err.message || 'An error occurred';
      setError(errorMsg);
      toast.error(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  const handleHistoryClick = (historyItem: QueryHistory) => {
    setQuery(historyItem.query);
    toast.success('Query loaded from history');
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    toast.success('Copied to clipboard!');
  };

  const exportAnalysis = () => {
    if (!result) return;
    const content = `# Financial Analysis\n\n**Query:** ${result.query}\n\n**Companies:** ${result.companies_found.join(', ')}\n\n**Analysis:**\n\n${result.analysis}`;
    const blob = new Blob([content], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analysis-${Date.now()}.md`;
    a.click();
    toast.success('Analysis exported!');
  };

  const commands = [
    {
      id: 'analyze',
      label: 'New Analysis',
      icon: <Search size={18} />,
      shortcut: 'Ctrl+Enter',
      action: () => {
        if (query.trim()) handleAnalyze();
        else document.querySelector('textarea')?.focus();
      },
      category: 'Actions'
    },
    {
      id: 'upload',
      label: 'Upload File',
      icon: <Upload size={18} />,
      action: () => setActiveTab('upload'),
      category: 'Actions'
    },
    {
      id: 'analytics',
      label: 'Toggle Analytics',
      icon: <BarChart3 size={18} />,
      action: () => setShowAnalytics(!showAnalytics),
      category: 'View'
    },
    {
      id: 'export',
      label: 'Export Analysis',
      icon: <Download size={18} />,
      shortcut: 'Ctrl+E',
      action: exportAnalysis,
      category: 'Actions'
    }
  ];

  const totalQueries = history.length;
  const totalCost = formatCost(totalTokens);

  return (
    <div className="clean-app">
      <Toaster
        position="top-right"
        toastOptions={{
          style: {
            background: 'var(--clean-bg)',
            color: 'var(--clean-text-primary)',
            border: '1px solid var(--clean-border)',
            borderRadius: '8px',
            boxShadow: 'var(--shadow-lg)',
          },
        }}
      />

      {/* Clean Header */}
      <header className="clean-header">
        <div className="clean-header-content">
          <div className="clean-logo">
            <div className="clean-logo-icon">
              <TrendingUp size={18} />
            </div>
            <span>Financial Analyst</span>
          </div>
          <div className="clean-header-actions">
            <div className="clean-badge">
              <Zap size={14} />
              {totalTokens.toLocaleString()} tokens
            </div>
            <div className="clean-badge">
              {totalCost}
            </div>
            <button
              onClick={() => setCommandPaletteOpen(true)}
              className="clean-button-secondary"
              style={{ padding: '8px 12px', fontSize: '13px' }}
              title="Command Palette (Ctrl+K)"
            >
              <Command size={16} />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="clean-container" style={{ paddingTop: '32px', paddingBottom: '64px' }}>
        {/* Analytics Dashboard (Optional) */}
        <AnimatePresence>
          {showAnalytics && (
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              style={{ marginBottom: '32px' }}
            >
              <AnalyticsDashboard
                totalTokens={totalTokens}
                totalQueries={totalQueries}
                totalCost={parseFloat(totalCost.replace('$', '').replace('< ', '0'))}
              />
            </motion.div>
          )}
        </AnimatePresence>

        {/* Tab Navigation */}
        <div className="clean-tab">
          <button
            onClick={() => setActiveTab('analyze')}
            className={`clean-tab-button ${activeTab === 'analyze' ? 'active' : ''}`}
          >
            <Search size={18} />
            Analyze
          </button>
          <button
            onClick={() => setActiveTab('upload')}
            className={`clean-tab-button ${activeTab === 'upload' ? 'active' : ''}`}
          >
            <Upload size={18} />
            Upload & Process
          </button>
        </div>

        {/* Analyze Tab */}
        {activeTab === 'analyze' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {/* Query Templates */}
            {showTemplates && query === '' && (
              <QueryTemplates
                onSelectTemplate={(templateQuery) => {
                  setQuery(templateQuery);
                  setShowTemplates(false);
                  toast.success('Template loaded!');
                }}
              />
            )}

            {/* Comparison View */}
            {showComparison && comparisonCompanies.length > 0 && (
              <ComparisonView
                companies={comparisonCompanies}
                onRemoveCompany={(company) => {
                  setComparisonCompanies(prev => prev.filter(c => c !== company));
                }}
                onAddCompany={() => {
                  const newCompany = prompt('Enter company ticker:');
                  if (newCompany) {
                    setComparisonCompanies(prev => [...prev, newCompany.toUpperCase()]);
                  }
                }}
              />
            )}

            {/* Quick Insights */}
            {result && !loading && (
              <QuickInsights analysis={result.analysis} />
            )}

            {/* Query Input */}
            <div className="clean-card" style={{ marginBottom: '24px' }}>
              <div style={{ marginBottom: '20px' }}>
                <h2 className="clean-section-title">Ask Financial Questions</h2>
                <p className="clean-section-description">
                  Query 89+ companies' 10-K filings with AI-powered analysis
                </p>
              </div>

              <div style={{ marginBottom: '16px', position: 'relative' }}>
                <textarea
                  value={query}
                  onChange={(e) => {
                    setQuery(e.target.value);
                    setShowTemplates(false);
                  }}
                  onKeyDown={(e) => {
                    if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
                      e.preventDefault();
                      handleAnalyze();
                    }
                  }}
                  placeholder="Ask about financial data, compare companies, analyze trends...

Examples:
• What is Apple's revenue in 2024?
• Compare AWS and Azure revenue
• Tell me about Microsoft's business segments"
                  className="clean-textarea"
                  rows={8}
                />
                <div style={{
                  position: 'absolute',
                  bottom: '12px',
                  right: '12px',
                  fontSize: '12px',
                  color: 'var(--clean-text-tertiary)',
                  background: 'var(--clean-bg)',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}>
                  {query.length} characters
                </div>
              </div>

              {/* Smart Suggestions */}
              <SmartSuggestions
                query={query}
                onSelectSuggestion={(suggestion) => {
                  setQuery(suggestion);
                  setShowTemplates(false);
                }}
                companies={result?.companies_found || []}
              />

              {/* History Chips */}
              {history.length > 0 && (
                <div style={{ marginBottom: '16px' }}>
                  <div style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)', marginBottom: '8px', fontWeight: 500 }}>
                    Recent Queries
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                    {history.slice(0, 5).map((item) => (
                      <button
                        key={item.id}
                        onClick={() => handleHistoryClick(item)}
                        className="clean-chip"
                      >
                        {item.query.substring(0, 40)}...
                      </button>
                    ))}
                  </div>
                </div>
              )}

              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '12px', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                  <div style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)' }}>
                    <kbd style={{
                      padding: '2px 6px',
                      background: 'var(--clean-bg-secondary)',
                      border: '1px solid var(--clean-border)',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontFamily: 'monospace'
                    }}>Ctrl</kbd> + <kbd style={{
                      padding: '2px 6px',
                      background: 'var(--clean-bg-secondary)',
                      border: '1px solid var(--clean-border)',
                      borderRadius: '4px',
                      fontSize: '11px',
                      fontFamily: 'monospace'
                    }}>Enter</kbd> to analyze
                  </div>
                  {!showTemplates && (
                    <button
                      onClick={() => {
                        setShowTemplates(true);
                        setQuery('');
                      }}
                      className="clean-button-secondary"
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                    >
                      <FileText size={14} style={{ marginRight: '6px' }} />
                      Templates
                    </button>
                  )}
                  {result && result.companies_found.length > 0 && (
                    <button
                      onClick={() => {
                        setShowComparison(true);
                        setComparisonCompanies(result.companies_found);
                      }}
                      className="clean-button-secondary"
                      style={{ padding: '6px 12px', fontSize: '12px' }}
                    >
                      <BarChart3 size={14} style={{ marginRight: '6px' }} />
                      Compare
                    </button>
                  )}
                </div>
                <button
                  onClick={handleAnalyze}
                  disabled={loading || !query.trim()}
                  className="clean-button"
                  style={{
                    opacity: loading || !query.trim() ? 0.5 : 1,
                    cursor: loading || !query.trim() ? 'not-allowed' : 'pointer'
                  }}
                >
                  {loading ? (
                    <>
                      <Loader2 size={18} style={{ animation: 'spin 0.8s linear infinite' }} />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search size={18} />
                      Analyze
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Results */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  className="clean-card"
                  style={{
                    borderColor: 'var(--clean-error)',
                    background: 'rgba(239, 68, 68, 0.05)'
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                    <XCircle size={24} style={{ color: 'var(--clean-error)' }} />
                    <div>
                      <h3 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '4px' }}>Error</h3>
                      <p style={{ color: 'var(--clean-text-secondary)' }}>{error}</p>
                    </div>
                  </div>
                </motion.div>
              )}

              {loading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="clean-card"
                  style={{ textAlign: 'center', padding: '64px' }}
                >
                  <div className="clean-spinner" style={{ margin: '0 auto 24px' }} />
                  <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>Analyzing Financial Documents</h3>
                  <p style={{ color: 'var(--clean-text-tertiary)' }}>Processing your query with AI...</p>
                </motion.div>
              )}

              {result && !loading && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 20 }}
                  className="clean-card"
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px', flexWrap: 'wrap', gap: '16px' }}>
                    <div>
                      <h2 style={{ fontSize: '24px', fontWeight: 600, marginBottom: '12px' }}>Analysis Results</h2>
                      <div style={{ display: 'flex', gap: '8px', alignItems: 'center', flexWrap: 'wrap' }}>
                        {result.companies_found.map((ticker) => (
                          <span key={ticker} className="clean-badge" style={{ background: 'var(--clean-accent-light)', color: 'var(--clean-accent)', borderColor: 'var(--clean-accent)' }}>
                            {ticker}
                          </span>
                        ))}
                        <span style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)' }}>
                          {result.metadata.total_files} file{result.metadata.total_files !== 1 ? 's' : ''}
                        </span>
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <button
                        onClick={() => copyToClipboard(result.analysis)}
                        className="clean-button-secondary"
                        style={{ padding: '8px 16px', fontSize: '13px' }}
                      >
                        <Copy size={16} style={{ marginRight: '6px' }} />
                        Copy
                      </button>
                      <button
                        onClick={exportAnalysis}
                        className="clean-button-secondary"
                        style={{ padding: '8px 16px', fontSize: '13px' }}
                      >
                        <Download size={16} style={{ marginRight: '6px' }} />
                        Export
                      </button>
                    </div>
                  </div>

                  <div className="clean-scrollbar" style={{
                    maxHeight: '600px',
                    overflowY: 'auto',
                    padding: '24px',
                    background: 'var(--clean-bg-secondary)',
                    borderRadius: '8px',
                    border: '1px solid var(--clean-border)'
                  }}>
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {result.analysis}
                    </ReactMarkdown>
                  </div>

                  {result.metadata.companies.length > 0 && (
                    <div style={{
                      marginTop: '24px',
                      paddingTop: '24px',
                      borderTop: '1px solid var(--clean-border)'
                    }}>
                      <div style={{ fontSize: '12px', color: 'var(--clean-text-tertiary)', marginBottom: '12px', textTransform: 'uppercase', letterSpacing: '0.5px', fontWeight: 600 }}>
                        Sources
                      </div>
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                        {result.metadata.companies.map((c, idx) => (
                          <span key={idx} className="clean-chip">
                            {c.ticker} ({formatBytes(c.content_length)})
                          </span>
                        ))}
                      </div>
                    </div>
                  )}
                </motion.div>
              )}

              {!result && !loading && !error && (
                <div className="clean-card" style={{ textAlign: 'center', padding: '64px' }}>
                  <BarChart3 size={64} style={{ margin: '0 auto 24px', color: 'var(--clean-text-tertiary)', opacity: 0.5 }} />
                  <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>Ready to Analyze</h3>
                  <p style={{ color: 'var(--clean-text-tertiary)' }}>Enter a query above to analyze financial documents</p>
                </div>
              )}
            </AnimatePresence>
          </motion.div>
        )}

        {/* Upload Tab */}
        {activeTab === 'upload' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            <FileUpload />
          </motion.div>
        )}
      </main>

      {/* Command Palette */}
      <CommandPalette
        isOpen={commandPaletteOpen}
        onClose={() => setCommandPaletteOpen(false)}
        commands={commands}
      />

      <style>{`
        @keyframes spin {
          from { transform: rotate(0deg); }
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
}

export default App;
