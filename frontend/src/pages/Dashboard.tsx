import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Activity, Shield, Database, TrendingUp } from 'lucide-react';
import { Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';

export default function Dashboard() {
  const { data: stats } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/users/me/stats`);
      return response.data;
    },
  });

  const { data: recentScans } = useQuery({
    queryKey: ['recent-scans'],
    queryFn: async () => {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/scans?limit=5`);
      return response.data.scans;
    },
  });

  const statCards = [
    {
      title: 'Total Scans',
      value: stats?.totalScans || 0,
      icon: Activity,
      color: 'text-cyber-primary',
      bgColor: 'bg-cyber-primary/10',
    },
    {
      title: 'IOCs Detected',
      value: stats?.totalIOCs || 0,
      icon: Shield,
      color: 'text-cyber-danger',
      bgColor: 'bg-cyber-danger/10',
    },
    {
      title: 'Entities',
      value: stats?.totalEntities || 0,
      icon: Database,
      color: 'text-cyber-accent',
      bgColor: 'bg-cyber-accent/10',
    },
    {
      title: 'Active Scans',
      value: recentScans?.filter((s: any) => s.status === 'RUNNING').length || 0,
      icon: TrendingUp,
      color: 'text-cyber-warning',
      bgColor: 'bg-cyber-warning/10',
    },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold glow-text">Intelligence Dashboard</h1>
        <p className="text-gray-400 mt-2">Real-time cyber threat intelligence overview</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <div key={stat.title} className="cyber-card">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-400">{stat.title}</p>
                <p className="text-3xl font-bold mt-2">{stat.value}</p>
              </div>
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Recent Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Scans */}
        <div className="cyber-card">
          <h2 className="text-xl font-bold mb-4">Recent Scans</h2>
          <div className="space-y-3">
            {recentScans?.map((scan: any) => (
              <div
                key={scan.id}
                className="flex items-center justify-between p-3 bg-cyber-bg rounded border border-cyber-border"
              >
                <div>
                  <p className="font-medium">{scan.target}</p>
                  <p className="text-sm text-gray-400">{scan.targetType}</p>
                </div>
                <span
                  className={`cyber-badge ${
                    scan.status === 'COMPLETED'
                      ? 'bg-cyber-accent/20 text-cyber-accent'
                      : scan.status === 'RUNNING'
                        ? 'bg-cyber-warning/20 text-cyber-warning'
                        : 'bg-gray-500/20 text-gray-400'
                  }`}
                >
                  {scan.status}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Activity Chart */}
        <div className="cyber-card">
          <h2 className="text-xl font-bold mb-4">Scan Activity</h2>
          <ResponsiveContainer width="100%" height={200}>
            <LineChart data={[]}>
              <XAxis dataKey="date" stroke="#6b7280" />
              <YAxis stroke="#6b7280" />
              <Tooltip
                contentStyle={{
                  backgroundColor: '#151932',
                  border: '1px solid #1e2442',
                  borderRadius: '8px',
                }}
              />
              <Line type="monotone" dataKey="scans" stroke="#00f0ff" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}
