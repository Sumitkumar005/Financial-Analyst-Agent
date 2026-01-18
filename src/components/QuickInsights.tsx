import { Sparkles, TrendingUp, AlertTriangle, DollarSign, Zap } from 'lucide-react';
import '../styles/clean.css';

interface Insight {
  id: string;
  type: 'positive' | 'warning' | 'info';
  title: string;
  description: string;
  icon: React.ReactNode;
}

interface QuickInsightsProps {
  analysis: string;
}

export default function QuickInsights({ analysis }: QuickInsightsProps) {
  // Extract insights from analysis (simplified - in production, use AI)
  const extractInsights = (text: string): Insight[] => {
    const insights: Insight[] = [];
    const lowerText = text.toLowerCase();

    // Revenue insights
    if (lowerText.includes('revenue') && (lowerText.includes('increase') || lowerText.includes('grow'))) {
      insights.push({
        id: 'revenue-growth',
        type: 'positive',
        title: 'Revenue Growth Detected',
        description: 'Company shows positive revenue trends',
        icon: <TrendingUp size={20} />
      });
    }

    // Risk insights
    if (lowerText.includes('risk') || lowerText.includes('uncertainty')) {
      insights.push({
        id: 'risks',
        type: 'warning',
        title: 'Risk Factors Identified',
        description: 'Several risk factors mentioned in analysis',
        icon: <AlertTriangle size={20} />
      });
    }

    // Financial health
    if (lowerText.includes('profit') || lowerText.includes('income')) {
      insights.push({
        id: 'profitability',
        type: 'info',
        title: 'Profitability Analysis',
        description: 'Financial performance metrics available',
        icon: <DollarSign size={20} />
      });
    }

    return insights;
  };

  const insights = extractInsights(analysis);

  if (insights.length === 0) return null;

  const getColor = (type: string) => {
    switch (type) {
      case 'positive': return { bg: 'rgba(16, 185, 129, 0.1)', border: '#10b981', text: '#059669' };
      case 'warning': return { bg: 'rgba(245, 158, 11, 0.1)', border: '#f59e0b', text: '#d97706' };
      default: return { bg: 'rgba(59, 130, 246, 0.1)', border: '#3b82f6', text: '#2563eb' };
    }
  };

  return (
    <div className="clean-card" style={{ marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '20px' }}>
        <Sparkles size={20} style={{ color: 'var(--clean-accent)' }} />
        <h3 style={{ fontSize: '18px', fontWeight: 600, margin: 0 }}>Quick Insights</h3>
      </div>
      
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(250px, 1fr))', gap: '12px' }}>
        {insights.map(insight => {
          const colors = getColor(insight.type);
          return (
            <div
              key={insight.id}
              style={{
                padding: '16px',
                background: colors.bg,
                border: `1px solid ${colors.border}`,
                borderRadius: '8px',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-md)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <div style={{ color: colors.border }}>
                  {insight.icon}
                </div>
                <div style={{ fontSize: '15px', fontWeight: 600, color: colors.text }}>
                  {insight.title}
                </div>
              </div>
              <div style={{ fontSize: '13px', color: 'var(--clean-text-secondary)', lineHeight: 1.5 }}>
                {insight.description}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
