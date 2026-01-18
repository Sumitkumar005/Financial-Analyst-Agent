import { useState } from 'react';
import { X, Plus, BarChart3, TrendingUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line } from 'recharts';
import '../styles/clean.css';

interface ComparisonViewProps {
  companies: string[];
  onRemoveCompany: (company: string) => void;
  onAddCompany: () => void;
  comparisonData?: any[];
}

export default function ComparisonView({ 
  companies, 
  onRemoveCompany, 
  onAddCompany,
  comparisonData 
}: ComparisonViewProps) {
  const [viewMode, setViewMode] = useState<'table' | 'chart'>('chart');

  // Mock data for demonstration
  const mockData = companies.map(company => ({
    company,
    revenue: Math.random() * 500 + 100,
    profit: Math.random() * 100 + 10,
    growth: (Math.random() * 20 - 5).toFixed(1)
  }));

  return (
    <div className="clean-card" style={{ marginBottom: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '24px' }}>
        <div>
          <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '4px' }}>Company Comparison</h3>
          <p style={{ fontSize: '14px', color: 'var(--clean-text-tertiary)' }}>
            Compare financial metrics side-by-side
          </p>
        </div>
        <div style={{ display: 'flex', gap: '8px' }}>
          <button
            onClick={() => setViewMode('table')}
            className="clean-button-secondary"
            style={{
              padding: '8px 16px',
              fontSize: '13px',
              background: viewMode === 'table' ? 'var(--clean-accent-light)' : 'var(--clean-bg)',
              borderColor: viewMode === 'table' ? 'var(--clean-accent)' : 'var(--clean-border)'
            }}
          >
            Table
          </button>
          <button
            onClick={() => setViewMode('chart')}
            className="clean-button-secondary"
            style={{
              padding: '8px 16px',
              fontSize: '13px',
              background: viewMode === 'chart' ? 'var(--clean-accent-light)' : 'var(--clean-bg)',
              borderColor: viewMode === 'chart' ? 'var(--clean-accent)' : 'var(--clean-border)'
            }}
          >
            Chart
          </button>
        </div>
      </div>

      {/* Company Tags */}
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '24px' }}>
        {companies.map(company => (
          <div
            key={company}
            className="clean-badge"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              background: 'var(--clean-accent-light)',
              borderColor: 'var(--clean-accent)',
              color: 'var(--clean-accent)',
              fontWeight: 600
            }}
          >
            {company}
            <button
              onClick={() => onRemoveCompany(company)}
              style={{
                background: 'none',
                border: 'none',
                cursor: 'pointer',
                padding: '2px',
                display: 'flex',
                alignItems: 'center',
                color: 'var(--clean-accent)'
              }}
            >
              <X size={14} />
            </button>
          </div>
        ))}
        <button
          onClick={onAddCompany}
          className="clean-chip"
          style={{
            borderStyle: 'dashed',
            borderColor: 'var(--clean-border)',
            color: 'var(--clean-text-tertiary)',
            cursor: 'pointer'
          }}
        >
          <Plus size={14} />
          Add Company
        </button>
      </div>

      {/* Chart View */}
      {viewMode === 'chart' && (
        <div style={{ marginBottom: '24px' }}>
          <h4 style={{ fontSize: '14px', fontWeight: 600, marginBottom: '16px', color: 'var(--clean-text-secondary)' }}>
            Revenue Comparison
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={mockData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--clean-border)" />
              <XAxis dataKey="company" stroke="var(--clean-text-tertiary)" />
              <YAxis stroke="var(--clean-text-tertiary)" />
              <Tooltip
                contentStyle={{
                  background: 'var(--clean-bg)',
                  border: '1px solid var(--clean-border)',
                  borderRadius: '8px'
                }}
              />
              <Bar dataKey="revenue" fill="var(--clean-accent)" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Table View */}
      {viewMode === 'table' && (
        <div style={{ overflowX: 'auto' }}>
          <table className="clean-table">
            <thead>
              <tr>
                <th>Company</th>
                <th>Revenue (B)</th>
                <th>Profit (B)</th>
                <th>Growth (%)</th>
              </tr>
            </thead>
            <tbody>
              {mockData.map((row, idx) => (
                <tr key={idx}>
                  <td style={{ fontWeight: 600 }}>{row.company}</td>
                  <td>${row.revenue.toFixed(1)}</td>
                  <td>${row.profit.toFixed(1)}</td>
                  <td>{row.growth}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {companies.length === 0 && (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--clean-text-tertiary)' }}>
          <BarChart3 size={48} style={{ margin: '0 auto 16px', opacity: 0.5 }} />
          <p>Add companies to start comparing</p>
        </div>
      )}
    </div>
  );
}
