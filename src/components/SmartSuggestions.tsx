import { useState, useEffect } from 'react';
import { Sparkles, TrendingUp, Search, Zap } from 'lucide-react';
import '../styles/clean.css';

interface Suggestion {
  id: string;
  text: string;
  type: 'company' | 'metric' | 'query' | 'comparison';
  icon: React.ReactNode;
}

interface SmartSuggestionsProps {
  query: string;
  onSelectSuggestion: (suggestion: string) => void;
  companies?: string[];
}

export default function SmartSuggestions({ query, onSelectSuggestion, companies = [] }: SmartSuggestionsProps) {
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);

  useEffect(() => {
    if (!query.trim()) {
      setSuggestions([]);
      return;
    }

    const newSuggestions: Suggestion[] = [];

    // Detect if user is typing a company name
    const companyKeywords = ['apple', 'microsoft', 'amazon', 'google', 'meta', 'tesla', 'nvidia', 'netflix'];
    const queryLower = query.toLowerCase();
    
    companyKeywords.forEach(company => {
      if (queryLower.includes(company) || company.includes(queryLower)) {
        const fullName = {
          'apple': 'Apple (AAPL)',
          'microsoft': 'Microsoft (MSFT)',
          'amazon': 'Amazon (AMZN)',
          'google': 'Alphabet (GOOGL)',
          'meta': 'Meta (META)',
          'tesla': 'Tesla (TSLA)',
          'nvidia': 'NVIDIA (NVDA)',
          'netflix': 'Netflix (NFLX)'
        }[company] || company;
        
        newSuggestions.push({
          id: `company-${company}`,
          text: `Analyze ${fullName}`,
          type: 'company',
          icon: <TrendingUp size={16} />
        });
      }
    });

    // Common query patterns
    if (queryLower.includes('compare') || queryLower.includes('vs')) {
      newSuggestions.push({
        id: 'compare-revenue',
        text: 'Compare revenue across companies',
        type: 'comparison',
        icon: <Sparkles size={16} />
      });
    }

    if (queryLower.includes('revenue') || queryLower.includes('sales')) {
      newSuggestions.push({
        id: 'revenue-trend',
        text: 'Show revenue trends over time',
        type: 'metric',
        icon: <TrendingUp size={16} />
      });
    }

    if (queryLower.includes('risk') || queryLower.includes('factor')) {
      newSuggestions.push({
        id: 'risk-analysis',
        text: 'Analyze risk factors',
        type: 'query',
        icon: <Search size={16} />
      });
    }

    // Generic suggestions
    if (newSuggestions.length === 0 && query.length > 3) {
      newSuggestions.push({
        id: 'general-1',
        text: `What is ${query}?`,
        type: 'query',
        icon: <Search size={16} />
      });
    }

    setSuggestions(newSuggestions.slice(0, 4));
  }, [query]);

  if (suggestions.length === 0) return null;

  return (
    <div style={{
      marginTop: '12px',
      padding: '12px',
      background: 'var(--clean-bg-secondary)',
      border: '1px solid var(--clean-border)',
      borderRadius: '8px'
    }}>
      <div style={{ 
        display: 'flex', 
        alignItems: 'center', 
        gap: '6px', 
        marginBottom: '8px',
        fontSize: '12px',
        color: 'var(--clean-text-tertiary)',
        fontWeight: 600
      }}>
        <Zap size={14} />
        Smart Suggestions
      </div>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
        {suggestions.map(suggestion => (
          <button
            key={suggestion.id}
            onClick={() => onSelectSuggestion(suggestion.text)}
            className="clean-chip"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              cursor: 'pointer',
              fontSize: '13px'
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--clean-accent-light)';
              e.currentTarget.style.borderColor = 'var(--clean-accent)';
              e.currentTarget.style.color = 'var(--clean-accent)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = '';
              e.currentTarget.style.borderColor = '';
              e.currentTarget.style.color = '';
            }}
          >
            {suggestion.icon}
            {suggestion.text}
          </button>
        ))}
      </div>
    </div>
  );
}
