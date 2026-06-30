import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Search } from 'lucide-react';

export default function EntityViewer() {
  const [search, setSearch] = useState('');
  const [type, setType] = useState('');

  const { data: entities, isLoading } = useQuery({
    queryKey: ['entities', search, type],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (search) params.append('q', search);
      if (type) params.append('type', type);

      const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/entities?${params}`);
      return response.data.entities;
    },
  });

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold glow-text">Entity Viewer</h1>
        <p className="text-gray-400 mt-2">Browse discovered entities and their relationships</p>
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
              placeholder="Search entities..."
            />
          </div>
          <select
            value={type}
            onChange={(e) => setType(e.target.value)}
            className="cyber-input w-48"
          >
            <option value="">All Types</option>
            <option value="IP">IP Address</option>
            <option value="DOMAIN">Domain</option>
            <option value="URL">URL</option>
            <option value="EMAIL">Email</option>
            <option value="HASH">Hash</option>
          </select>
        </div>
      </div>

      {/* Entities List */}
      <div className="cyber-card">
        {isLoading ? (
          <div className="text-center py-12 text-gray-400">Loading entities...</div>
        ) : entities?.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No entities found</div>
        ) : (
          <div className="space-y-3">
            {entities?.map((entity: any) => (
              <div
                key={entity.id}
                className="flex items-center justify-between p-4 bg-cyber-bg rounded border border-cyber-border hover:border-cyber-primary/50 transition-colors cursor-pointer"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <p className="font-semibold">{entity.value}</p>
                    <span className="cyber-badge bg-cyber-accent/20 text-cyber-accent">
                      {entity.type}
                    </span>
                  </div>
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                    <span>First seen: {new Date(entity.first_seen).toLocaleDateString()}</span>
                    <span>Last seen: {new Date(entity.last_seen).toLocaleDateString()}</span>
                  </div>
                </div>
                {entity.threat_level && (
                  <span className={`cyber-badge-${entity.threat_level.toLowerCase()}`}>
                    {entity.threat_level}
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
