import { useState } from 'react';
import { FileText, TrendingUp, BarChart3, AlertTriangle, DollarSign, Users, Zap } from 'lucide-react';
import '../styles/clean.css';

interface Template {
  id: string;
  title: string;
  description: string;
  query: string;
  icon: React.ReactNode;
  category: string;
  popular?: boolean;
}

const templates: Template[] = [
  {
    id: 'revenue-comparison',
    title: 'Compare Revenue',
    description: 'Compare revenue across multiple companies',
    query: 'Compare revenue of Apple, Microsoft, and Amazon for 2024',
    icon: <BarChart3 size={20} />,
    category: 'Comparison',
    popular: true
  },
  {
    id: 'risk-factors',
    title: 'Risk Factors',
    description: 'Analyze risk factors for a company',
    query: 'What are the main risk factors for Apple Inc?',
    icon: <AlertTriangle size={20} />,
    category: 'Analysis'
  },
  {
    id: 'business-overview',
    title: 'Business Overview',
    description: 'Get company business background',
    query: 'Tell me about the business and operations of Microsoft',
    icon: <FileText size={20} />,
    category: 'Overview',
    popular: true
  },
  {
    id: 'financial-metrics',
    title: 'Financial Metrics',
    description: 'Key financial ratios and metrics',
    query: 'What are the key financial metrics and ratios for Amazon?',
    icon: <DollarSign size={20} />,
    category: 'Metrics'
  },
  {
    id: 'segment-analysis',
    title: 'Segment Analysis',
    description: 'Analyze business segments',
    query: 'Break down the revenue by business segments for Apple',
    icon: <TrendingUp size={20} />,
    category: 'Analysis',
    popular: true
  },
  {
    id: 'board-directors',
    title: 'Board of Directors',
    description: 'Get board member information',
    query: 'Who are the board of directors at Microsoft and what are their backgrounds?',
    icon: <Users size={20} />,
    category: 'Governance'
  },
  {
    id: 'cash-flow',
    title: 'Cash Flow Analysis',
    description: 'Analyze cash flow statements',
    query: 'Show me the cash flow statement for Amazon for 2024',
    icon: <DollarSign size={20} />,
    category: 'Financials'
  },
  {
    id: 'growth-trends',
    title: 'Growth Trends',
    description: 'Analyze growth over time',
    query: 'What are the revenue growth trends for Apple over the past 3 years?',
    icon: <TrendingUp size={20} />,
    category: 'Trends',
    popular: true
  }
];

interface QueryTemplatesProps {
  onSelectTemplate: (query: string) => void;
}

export default function QueryTemplates({ onSelectTemplate }: QueryTemplatesProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const categories = ['all', ...Array.from(new Set(templates.map(t => t.category)))];

  const filteredTemplates = templates.filter(template => {
    const matchesCategory = selectedCategory === 'all' || template.category === selectedCategory;
    const matchesSearch = template.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  const popularTemplates = templates.filter(t => t.popular);

  return (
    <div className="clean-card" style={{ marginBottom: '24px' }}>
      <div style={{ marginBottom: '20px' }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '8px' }}>
          <h3 style={{ fontSize: '18px', fontWeight: 600, margin: 0 }}>Query Templates</h3>
          <span style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)' }}>
            {filteredTemplates.length} templates
          </span>
        </div>
        <p style={{ fontSize: '14px', color: 'var(--clean-text-tertiary)', margin: 0 }}>
          Start with a template or build your own query
        </p>
      </div>

      {/* Search */}
      <div style={{ marginBottom: '16px' }}>
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="Search templates..."
          className="clean-input"
          style={{ marginBottom: '12px' }}
        />
        
        {/* Category Filter */}
        <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap' }}>
          {categories.map(category => (
            <button
              key={category}
              onClick={() => setSelectedCategory(category)}
              className="clean-chip"
              style={{
                background: selectedCategory === category ? 'var(--clean-accent-light)' : 'var(--clean-bg-secondary)',
                borderColor: selectedCategory === category ? 'var(--clean-accent)' : 'var(--clean-border)',
                color: selectedCategory === category ? 'var(--clean-accent)' : 'var(--clean-text-secondary)',
                fontWeight: selectedCategory === category ? 600 : 500
              }}
            >
              {category.charAt(0).toUpperCase() + category.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Popular Templates */}
      {selectedCategory === 'all' && searchQuery === '' && (
        <div style={{ marginBottom: '24px' }}>
          <div style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)', marginBottom: '12px', fontWeight: 600 }}>
            ⭐ Popular Templates
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
            {popularTemplates.map(template => (
              <button
                key={template.id}
                onClick={() => onSelectTemplate(template.query)}
                className="clean-card"
                style={{
                  textAlign: 'left',
                  padding: '16px',
                  cursor: 'pointer',
                  border: '1px solid var(--clean-border)',
                  transition: 'all 0.2s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.borderColor = 'var(--clean-accent)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = 'var(--shadow-md)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.borderColor = 'var(--clean-border)';
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = 'none';
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                  <div style={{ color: 'var(--clean-accent)' }}>
                    {template.icon}
                  </div>
                  <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--clean-text-primary)' }}>
                    {template.title}
                  </div>
                </div>
                <div style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)', lineHeight: 1.5 }}>
                  {template.description}
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* All Templates */}
      <div>
        {selectedCategory !== 'all' || searchQuery !== '' ? (
          <div style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)', marginBottom: '12px', fontWeight: 600 }}>
            {selectedCategory !== 'all' ? `${selectedCategory} Templates` : 'Search Results'}
          </div>
        ) : (
          <div style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)', marginBottom: '12px', fontWeight: 600 }}>
            All Templates
          </div>
        )}
        
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '12px' }}>
          {filteredTemplates.map(template => (
            <button
              key={template.id}
              onClick={() => onSelectTemplate(template.query)}
              className="clean-card"
              style={{
                textAlign: 'left',
                padding: '16px',
                cursor: 'pointer',
                border: '1px solid var(--clean-border)',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = 'var(--clean-accent)';
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = 'var(--shadow-md)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = 'var(--clean-border)';
                e.currentTarget.style.transform = 'translateY(0)';
                e.currentTarget.style.boxShadow = 'none';
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
                <div style={{ color: 'var(--clean-accent)' }}>
                  {template.icon}
                </div>
                <div style={{ fontSize: '15px', fontWeight: 600, color: 'var(--clean-text-primary)' }}>
                  {template.title}
                </div>
                {template.popular && (
                  <span style={{
                    fontSize: '10px',
                    padding: '2px 6px',
                    background: 'var(--clean-accent-light)',
                    color: 'var(--clean-accent)',
                    borderRadius: '4px',
                    fontWeight: 600
                  }}>
                    Popular
                  </span>
                )}
              </div>
              <div style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)', lineHeight: 1.5, marginBottom: '8px' }}>
                {template.description}
              </div>
              <div style={{
                fontSize: '11px',
                color: 'var(--clean-text-tertiary)',
                padding: '4px 8px',
                background: 'var(--clean-bg-secondary)',
                borderRadius: '4px',
                display: 'inline-block',
                fontFamily: 'monospace'
              }}>
                {template.query.substring(0, 50)}...
              </div>
            </button>
          ))}
        </div>
      </div>

      {filteredTemplates.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--clean-text-tertiary)' }}>
          No templates found. Try a different search or category.
        </div>
      )}
    </div>
  );
}
