import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Search, Filter } from 'lucide-react';

export default function IOCViewer() {
  const [search, setSearch] = useState('');
  const [threatLevel, setThreatLevel] = useState('');

  const { data: iocs, isLoading } = useQuery({
    queryKey: ['iocs', search, threatLevel],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (search) params.append('q', search);
      if (threatLevel) params.append('threatLevel', threatLevel);

      const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/iocs?${params}`);
      return response.data.iocs;
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold glow-text">IOC Viewer</h1>
        <p className="text-gray-400 mt-2">Browse and analyze indicators of compromise</p>
      </div>

      {/* Filters */}
      <div className="cyber-card">
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="cyber-input pl-10"
              placeholder="Search IOCs..."
            />
          </div>
          <select
            value={threatLevel}
            onChange={(e) => setThreatLevel(e.target.value)}
            className="cyber-input w-48"
          >
            <option value="">All Threat Levels</option>
            <option value="CRITICAL">Critical</option>
            <option value="HIGH">High</option>
            <option value="MEDIUM">Medium</option>
            <option value="LOW">Low</option>
          </select>
        </div>
      </div>

      {/* IOCs List */}
      <div className="cyber-card">
        {isLoading ? (
          <div className="text-center py-12 text-gray-400">Loading IOCs...</div>
        ) : iocs?.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No IOCs found</div>
        ) : (
          <div className="space-y-3">
            {iocs?.map((ioc: any) => (
              <div
                key={ioc.id}
                className="flex items-center justify-between p-4 bg-cyber-bg rounded border border-cyber-border"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <p className="font-semibold">{ioc.value}</p>
                    <span className="cyber-badge bg-cyber-accent/20 text-cyber-accent">
                      {ioc.type}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                    <span>Source: {ioc.source}</span>
                    <span>Confidence: {ioc.confidence}%</span>
                  </div>
                </div>
                <span className={`cyber-badge-${ioc.threat_level.toLowerCase()}`}>
                  {ioc.threat_level}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
