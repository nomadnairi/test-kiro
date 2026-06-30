import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { ArrowLeft, Shield, Database, Network } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function ScanDetails() {
  const { scanId } = useParams();

  const { data: results, isLoading } = useQuery({
    queryKey: ['scan-results', scanId],
    queryFn: async () => {
      const response = await axios.get(
        `${import.meta.env.VITE_API_URL}/api/scans/${scanId}/results`
      );
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="text-center py-12">Loading scan results...</div>;
  }

  const scan = results?.scan;
  const entities = results?.entities || [];
  const iocs = results?.iocs || [];
  const relationships = results?.relationships || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Link to="/scans" className="p-2 hover:bg-cyber-surface rounded">
          <ArrowLeft className="w-5 h-5" />
        </Link>
        <div className="flex-1">
          <h1 className="text-3xl font-bold glow-text">{scan?.target}</h1>
          <p className="text-gray-400 mt-1">Scan Results</p>
        </div>
        <span
          className={`cyber-badge ${
            scan?.status === 'COMPLETED'
              ? 'bg-cyber-accent/20 text-cyber-accent'
              : scan?.status === 'RUNNING'
                ? 'bg-cyber-warning/20 text-cyber-warning'
                : 'bg-gray-500/20 text-gray-400'
          }`}
        >
          {scan?.status}
        </span>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="cyber-card">
          <div className="flex items-center gap-3">
            <Database className="w-8 h-8 text-cyber-primary" />
            <div>
              <p className="text-sm text-gray-400">Entities</p>
              <p className="text-2xl font-bold">{entities.length}</p>
            </div>
          </div>
        </div>
        <div className="cyber-card">
          <div className="flex items-center gap-3">
            <Shield className="w-8 h-8 text-cyber-danger" />
            <div>
              <p className="text-sm text-gray-400">IOCs</p>
              <p className="text-2xl font-bold">{iocs.length}</p>
            </div>
          </div>
        </div>
        <div className="cyber-card">
          <div className="flex items-center gap-3">
            <Network className="w-8 h-8 text-cyber-accent" />
            <div>
              <p className="text-sm text-gray-400">Relationships</p>
              <p className="text-2xl font-bold">{relationships.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Entities */}
      <div className="cyber-card">
        <h2 className="text-xl font-bold mb-4">Discovered Entities</h2>
        <div className="space-y-2">
          {entities.slice(0, 10).map((entity: any) => (
            <div
              key={entity.id}
              className="flex items-center justify-between p-3 bg-cyber-bg rounded border border-cyber-border"
            >
              <div>
                <p className="font-medium">{entity.value}</p>
                <p className="text-sm text-gray-400">{entity.type}</p>
              </div>
              {entity.threat_level && (
                <span className={`cyber-badge-${entity.threat_level.toLowerCase()}`}>
                  {entity.threat_level}
                </span>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* IOCs */}
      {iocs.length > 0 && (
        <div className="cyber-card">
          <h2 className="text-xl font-bold mb-4">Indicators of Compromise</h2>
          <div className="space-y-2">
            {iocs.map((ioc: any) => (
              <div
                key={ioc.id}
                className="flex items-center justify-between p-3 bg-cyber-bg rounded border border-cyber-danger/30"
              >
                <div>
                  <p className="font-medium">{ioc.value}</p>
                  <p className="text-sm text-gray-400">{ioc.source}</p>
                </div>
                <span className={`cyber-badge-${ioc.threat_level.toLowerCase()}`}>
                  {ioc.threat_level}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
