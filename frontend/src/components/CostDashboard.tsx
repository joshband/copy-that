/**
 * Cost Dashboard Component
 *
 * Displays cost breakdown across GCP, Neon, Anthropic, and OpenAI
 * Tracks budget and provides optimization recommendations
 */

import React, { useState, useEffect } from 'react';
import axios from 'axios';

interface ServiceCost {
  service_name: string;
  provider: string;
  cost_usd: number;
  usage?: string;
  period: string;
  last_updated: string;
}

interface CostSummary {
  total_cost_usd: number;
  period_start: string;
  period_end: string;
  breakdown_by_provider: Record<string, number>;
  breakdown_by_service: ServiceCost[];
  budget_limit_usd?: number;
  budget_remaining_usd?: number;
  alerts: string[];
}

export const CostDashboard: React.FC = () => {
  const [summary, setSummary] = useState<CostSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [period, setPeriod] = useState<'today' | 'this_week' | 'this_month'>('this_month');
  const [budget, setBudget] = useState<number>(50); // Default $50/month budget

  useEffect(() => {
    fetchCostSummary();
  }, [period, budget]);

  const fetchCostSummary = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.get<CostSummary>(
        `/api/v1/costs/summary`,
        {
          params: {
            period,
            budget_usd: budget
          }
        }
      );
      setSummary(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to fetch cost data');
      console.error('Cost fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="cost-dashboard loading">
        <div className="spinner">Loading cost data...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="cost-dashboard error">
        <h3>❌ Error Loading Costs</h3>
        <p>{error}</p>
        <button onClick={fetchCostSummary}>Retry</button>
      </div>
    );
  }

  if (!summary) {
    return null;
  }

  const budgetPercentage = summary.budget_limit_usd
    ? (summary.total_cost_usd / summary.budget_limit_usd) * 100
    : 0;

  return (
    <div className="cost-dashboard">
      {/* Header */}
      <div className="dashboard-header">
        <h2>💰 Cost Dashboard</h2>
        <div className="controls">
          <select value={period} onChange={(e) => setPeriod(e.target.value as any)}>
            <option value="today">Today</option>
            <option value="this_week">This Week</option>
            <option value="this_month">This Month</option>
          </select>
          <input
            type="number"
            value={budget}
            onChange={(e) => setBudget(Number(e.target.value))}
            placeholder="Monthly Budget ($)"
            className="budget-input"
          />
        </div>
      </div>

      {/* Alerts */}
      {summary.alerts.length > 0 && (
        <div className="alerts">
          {summary.alerts.map((alert, idx) => (
            <div
              key={idx}
              className={`alert ${
                alert.includes('OVER') ? 'alert-danger' :
                alert.includes('Warning') ? 'alert-warning' :
                'alert-info'
              }`}
            >
              {alert}
            </div>
          ))}
        </div>
      )}

      {/* Total Cost Card */}
      <div className="cost-summary-card">
        <div className="total-cost">
          <h3>Total Cost</h3>
          <div className="cost-amount">${summary.total_cost_usd.toFixed(2)}</div>
          <div className="cost-period">
            {new Date(summary.period_start).toLocaleDateString()} -
            {new Date(summary.period_end).toLocaleDateString()}
          </div>
        </div>

        {summary.budget_limit_usd && (
          <div className="budget-progress">
            <div className="budget-bar">
              <div
                className={`budget-fill ${budgetPercentage > 100 ? 'over-budget' : budgetPercentage > 80 ? 'warning' : 'good'}`}
                style={{ width: `${Math.min(budgetPercentage, 100)}%` }}
              />
            </div>
            <div className="budget-text">
              ${summary.total_cost_usd.toFixed(2)} / ${summary.budget_limit_usd.toFixed(2)}
              ({budgetPercentage.toFixed(1)}%)
            </div>
          </div>
        )}
      </div>

      {/* Provider Breakdown */}
      <div className="provider-breakdown">
        <h3>Cost by Provider</h3>
        <div className="provider-grid">
          {Object.entries(summary.breakdown_by_provider).map(([provider, cost]) => (
            <div key={provider} className="provider-card">
              <div className="provider-name">
                {provider === 'GCP' && '☁️'}
                {provider === 'Neon' && '🐘'}
                {provider === 'Anthropic' && '🤖'}
                {provider === 'OpenAI' && '🧠'}
                {' '}{provider}
              </div>
              <div className="provider-cost">${cost.toFixed(2)}</div>
              <div className="provider-percentage">
                {((cost / summary.total_cost_usd) * 100).toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Service Breakdown */}
      <div className="service-breakdown">
        <h3>Cost by Service</h3>
        <div className="service-table">
          <table>
            <thead>
              <tr>
                <th>Service</th>
                <th>Provider</th>
                <th>Usage</th>
                <th>Cost</th>
              </tr>
            </thead>
            <tbody>
              {summary.breakdown_by_service.map((service, idx) => (
                <tr key={idx}>
                  <td>{service.service_name}</td>
                  <td>
                    <span className={`provider-badge ${service.provider.toLowerCase()}`}>
                      {service.provider}
                    </span>
                  </td>
                  <td className="usage-metric">{service.usage || 'N/A'}</td>
                  <td className="cost-cell">${service.cost_usd.toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
            <tfoot>
              <tr>
                <td colSpan={3}><strong>Total</strong></td>
                <td className="cost-cell">
                  <strong>${summary.total_cost_usd.toFixed(2)}</strong>
                </td>
              </tr>
            </tfoot>
          </table>
        </div>
      </div>

      {/* Optimization Tips */}
      <div className="optimization-tips">
        <h3>💡 Cost Optimization Tips</h3>
        <ul>
          <li>✅ Cloud Run min-instances=0 (saves $40-60/month)</li>
          <li>✅ Using Neon free tier (saves $25-50/month)</li>
          <li>✅ Multi-stage Docker builds (reduces storage costs)</li>
          <li>📊 Monitor Claude API usage - batch requests when possible</li>
          <li>🎯 Current monthly run rate: ${(summary.total_cost_usd * 30).toFixed(2)}</li>
        </ul>
      </div>

      {/* Refresh Button */}
      <button onClick={fetchCostSummary} className="refresh-button">
        🔄 Refresh Costs
      </button>

      <style jsx>{`
        .cost-dashboard {
          max-width: 1200px;
          margin: 0 auto;
          padding: 24px;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        }

        .dashboard-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          margin-bottom: 24px;
        }

        .dashboard-header h2 {
          margin: 0;
          font-size: 28px;
        }

        .controls {
          display: flex;
          gap: 12px;
        }

        .controls select,
        .budget-input {
          padding: 8px 12px;
          border: 1px solid #ddd;
          border-radius: 6px;
          font-size: 14px;
        }

        .alerts {
          margin-bottom: 24px;
        }

        .alert {
          padding: 12px 16px;
          border-radius: 8px;
          margin-bottom: 8px;
        }

        .alert-danger {
          background: #fee;
          color: #c00;
          border-left: 4px solid #c00;
        }

        .alert-warning {
          background: #ffc;
          color: #860;
          border-left: 4px solid #f90;
        }

        .alert-info {
          background: #e7f3ff;
          color: #06c;
          border-left: 4px solid #06c;
        }

        .cost-summary-card {
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          padding: 32px;
          border-radius: 16px;
          margin-bottom: 24px;
        }

        .total-cost {
          text-align: center;
        }

        .total-cost h3 {
          margin: 0 0 8px 0;
          opacity: 0.9;
          font-size: 16px;
          font-weight: 500;
        }

        .cost-amount {
          font-size: 48px;
          font-weight: 700;
          margin: 8px 0;
        }

        .cost-period {
          opacity: 0.8;
          font-size: 14px;
        }

        .budget-progress {
          margin-top: 24px;
        }

        .budget-bar {
          background: rgba(255, 255, 255, 0.3);
          height: 8px;
          border-radius: 4px;
          overflow: hidden;
        }

        .budget-fill {
          height: 100%;
          transition: width 0.3s ease, background-color 0.3s ease;
        }

        .budget-fill.good {
          background: #4caf50;
        }

        .budget-fill.warning {
          background: #ff9800;
        }

        .budget-fill.over-budget {
          background: #f44336;
        }

        .budget-text {
          margin-top: 8px;
          text-align: center;
          font-size: 14px;
          opacity: 0.9;
        }

        .provider-breakdown,
        .service-breakdown,
        .optimization-tips {
          background: white;
          border: 1px solid #e0e0e0;
          border-radius: 12px;
          padding: 24px;
          margin-bottom: 24px;
        }

        .provider-breakdown h3,
        .service-breakdown h3,
        .optimization-tips h3 {
          margin: 0 0 16px 0;
          font-size: 18px;
        }

        .provider-grid {
          display: grid;
          grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
          gap: 16px;
        }

        .provider-card {
          background: #f8f9fa;
          padding: 20px;
          border-radius: 8px;
          text-align: center;
          border: 2px solid transparent;
          transition: all 0.2s;
        }

        .provider-card:hover {
          border-color: #667eea;
          transform: translateY(-2px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }

        .provider-name {
          font-size: 16px;
          font-weight: 600;
          margin-bottom: 8px;
          color: #333;
        }

        .provider-cost {
          font-size: 28px;
          font-weight: 700;
          color: #667eea;
          margin-bottom: 4px;
        }

        .provider-percentage {
          font-size: 14px;
          color: #666;
        }

        .service-table {
          overflow-x: auto;
        }

        .service-table table {
          width: 100%;
          border-collapse: collapse;
        }

        .service-table th,
        .service-table td {
          text-align: left;
          padding: 12px;
          border-bottom: 1px solid #e0e0e0;
        }

        .service-table th {
          background: #f8f9fa;
          font-weight: 600;
          color: #333;
        }

        .service-table tbody tr:hover {
          background: #f8f9fa;
        }

        .provider-badge {
          display: inline-block;
          padding: 4px 8px;
          border-radius: 4px;
          font-size: 12px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .provider-badge.gcp {
          background: #4285f4;
          color: white;
        }

        .provider-badge.neon {
          background: #00e699;
          color: #000;
        }

        .provider-badge.anthropic {
          background: #b76e00;
          color: white;
        }

        .provider-badge.openai {
          background: #10a37f;
          color: white;
        }

        .usage-metric {
          font-size: 13px;
          color: #666;
        }

        .cost-cell {
          font-weight: 600;
          color: #333;
          text-align: right;
        }

        .optimization-tips ul {
          margin: 0;
          padding-left: 20px;
        }

        .optimization-tips li {
          margin-bottom: 8px;
          line-height: 1.6;
        }

        .refresh-button {
          background: #667eea;
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: 8px;
          font-size: 14px;
          font-weight: 600;
          cursor: pointer;
          transition: all 0.2s;
          width: 100%;
        }

        .refresh-button:hover {
          background: #5568d3;
          transform: translateY(-1px);
          box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
        }

        .loading,
        .error {
          text-align: center;
          padding: 48px;
        }

        .spinner {
          font-size: 18px;
          color: #666;
        }

        tfoot td {
          font-size: 16px;
          padding-top: 16px;
          border-top: 2px solid #333;
        }
      `}</style>
    </div>
  );
};

export default CostDashboard;
