import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import axios from 'axios';
import { Plus, Eye } from 'lucide-react';

export default function Scans() {
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [target, setTarget] = useState('');
  const queryClient = useQueryClient();

  const { data: scans, isLoading } = useQuery({
    queryKey: ['scans'],
    queryFn: async () => {
      const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/scans`);
      return response.data.scans;
    },
  });

  const createScan = useMutation({
    mutationFn: async (target: string) => {
      const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/scans`, {
        target,
        autoRecon: true,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['scans'] });
      setShowCreateModal(false);
      setTarget('');
    },
  });

  const handleCreateScan = (e: React.FormEvent) => {
    e.preventDefault();
    createScan.mutate(target);
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold glow-text">Scans</h1>
          <p className="text-gray-400 mt-2">Manage and monitor intelligence scans</p>
        </div>
        <button onClick={() => setShowCreateModal(true)} className="cyber-button flex items-center gap-2">
          <Plus className="w-5 h-5" />
          New Scan
        </button>
      </div>

      {/* Scans List */}
      <div className="cyber-card">
        {isLoading ? (
          <div className="text-center py-12 text-gray-400">Loading scans...</div>
        ) : scans?.length === 0 ? (
          <div className="text-center py-12 text-gray-400">No scans yet. Create your first scan!</div>
        ) : (
          <div className="space-y-3">
            {scans?.map((scan: any) => (
              <div
                key={scan.id}
                className="flex items-center justify-between p-4 bg-cyber-bg rounded border border-cyber-border hover:border-cyber-primary/50 transition-colors"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-semibold text-lg">{scan.target}</h3>
                    <span className="cyber-badge bg-cyber-accent/20 text-cyber-accent">
                      {scan.target_type}
                    </span>
                    <span
                      className={`cyber-badge ${
                        scan.status === 'COMPLETED'
                          ? 'bg-cyber-accent/20 text-cyber-accent'
                          : scan.status === 'RUNNING'
                          ? 'bg-cyber-warning/20 text-cyber-warning'
                          : scan.status === 'FAILED'
                          ? 'bg-cyber-danger/20 text-cyber-danger'
                          : 'bg-gray-500/20 text-gray-400'
                      }`}
                    >
                      {scan.status}
                    </span>
                  </div>
                  <div className="flex items-center gap-6 mt-2 text-sm text-gray-400">
                    <span>Entities: {scan.entity_count || 0}</span>
                    <span>IOCs: {scan.ioc_count || 0}</span>
                    <span>Progress: {scan.progress}%</span>
                  </div>
                </div>
                <Link
                  to={`/scans/${scan.id}`}
                  className="cyber-button-secondary flex items-center gap-2"
                >
                  <Eye className="w-4 h-4" />
                  View
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Create Scan Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="cyber-card max-w-md w-full">
            <h2 className="text-2xl font-bold mb-4">Create New Scan</h2>
            <form onSubmit={handleCreateScan} className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-2">Target</label>
                <input
                  type="text"
                  value={target}
                  onChange={(e) => setTarget(e.target.value)}
                  className="cyber-input"
                  placeholder="example.com or 1.2.3.4"
                  required
                />
                <p className="text-xs text-gray-500 mt-1">
                  Enter a domain, IP address, or URL to scan
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  type="submit"
                  disabled={createScan.isPending}
                  className="cyber-button flex-1"
                >
                  {createScan.isPending ? 'Creating...' : 'Start Scan'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="cyber-button-secondary flex-1"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
