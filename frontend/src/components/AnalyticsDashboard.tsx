import { TrendingUp, Zap, FileText, DollarSign } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface AnalyticsDashboardProps {
  totalTokens: number;
  totalQueries: number;
  totalCost: number;
  recentActivity?: Array<{ date: string; tokens: number; cost: number }>;
}

export default function AnalyticsDashboard({ totalTokens, totalQueries, totalCost, recentActivity = [] }: AnalyticsDashboardProps) {
  const formatCost = (cost: number) => {
    return cost < 0.01 ? '< $0.01' : `$${cost.toFixed(4)}`;
  };

  const formatNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toString();
  };

  const chartData = recentActivity.length > 0 ? recentActivity : [
    { date: 'Mon', tokens: 0, cost: 0 },
    { date: 'Tue', tokens: 0, cost: 0 },
    { date: 'Wed', tokens: 0, cost: 0 },
    { date: 'Thu', tokens: 0, cost: 0 },
    { date: 'Fri', tokens: 0, cost: 0 },
    { date: 'Sat', tokens: 0, cost: 0 },
    { date: 'Sun', tokens: 0, cost: 0 },
  ];

  const stats = [
    {
      label: 'Total Tokens',
      value: formatNumber(totalTokens),
      icon: Zap,
      color: 'var(--premium-accent-primary)',
      trend: '+12%'
    },
    {
      label: 'Queries',
      value: totalQueries.toString(),
      icon: FileText,
      color: 'var(--premium-accent-secondary)',
      trend: '+5%'
    },
    {
      label: 'Total Cost',
      value: formatCost(totalCost),
      icon: DollarSign,
      color: 'var(--premium-accent-gold)',
      trend: '-8%'
    },
    {
      label: 'Avg per Query',
      value: totalQueries > 0 ? formatCost(totalCost / totalQueries) : '$0.00',
      icon: TrendingUp,
      color: 'var(--premium-accent-cyan)',
      trend: '-3%'
    }
  ];

  return (
    <div className="clean-card" style={{ marginBottom: '24px' }}>
      <div style={{ marginBottom: '24px' }}>
        <h3 style={{ fontSize: '18px', fontWeight: 600, marginBottom: '8px' }}>Analytics Dashboard</h3>
        <p style={{ fontSize: '14px', color: 'var(--premium-text-tertiary)' }}>
          Real-time usage statistics and insights
        </p>
      </div>

      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
        gap: '16px',
        marginBottom: '32px'
      }}>
        {stats.map((stat, index) => {
          const Icon = stat.icon;
          return (
            <div
              key={index}
              className="clean-card"
              style={{
                padding: '20px',
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
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '12px' }}>
                <div style={{
                  width: '40px',
                  height: '40px',
                  borderRadius: '8px',
                  background: `${stat.color}15`,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: stat.color
                }}>
                  <Icon size={20} />
                </div>
                <span style={{
                  fontSize: '12px',
                  color: 'var(--clean-success)',
                  fontWeight: 600,
                  background: 'rgba(16, 185, 129, 0.1)',
                  padding: '4px 8px',
                  borderRadius: '4px'
                }}>
                  {stat.trend}
                </span>
              </div>
              <div style={{ fontSize: '24px', fontWeight: 700, marginBottom: '4px', color: 'var(--clean-text-primary)' }}>
                {stat.value}
              </div>
              <div style={{ fontSize: '13px', color: 'var(--clean-text-tertiary)' }}>
                {stat.label}
              </div>
            </div>
          );
        })}
      </div>

      {recentActivity.length > 0 && (
        <div style={{ marginTop: '32px' }}>
          <h4 style={{ fontSize: '16px', fontWeight: 600, marginBottom: '16px' }}>Usage Trend</h4>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--premium-border)" />
              <XAxis dataKey="date" stroke="var(--premium-text-tertiary)" />
              <YAxis stroke="var(--premium-text-tertiary)" />
              <Tooltip
                contentStyle={{
                  background: 'var(--clean-bg)',
                  border: '1px solid var(--clean-border)',
                  borderRadius: '8px',
                  color: 'var(--clean-text-primary)'
                }}
              />
              <Line
                type="monotone"
                dataKey="tokens"
                stroke="var(--clean-accent)"
                strokeWidth={2}
                dot={{ fill: 'var(--clean-accent)', r: 4 }}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
