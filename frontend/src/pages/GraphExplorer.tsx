import { useEffect, useRef } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';

cytoscape.use(dagre);

export default function GraphExplorer() {
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      style: [
        {
          selector: 'node',
          style: {
            'background-color': '#00f0ff',
            label: 'data(label)',
            color: '#fff',
            'text-valign': 'center',
            'text-halign': 'center',
            'font-size': '12px',
            width: '60px',
            height: '60px',
          },
        },
        {
          selector: 'edge',
          style: {
            width: 2,
            'line-color': '#1e2442',
            'target-arrow-color': '#1e2442',
            'target-arrow-shape': 'triangle',
            'curve-style': 'bezier',
          },
        },
      ],
      elements: [
        // Sample data - replace with real data
        { data: { id: '1', label: 'example.com' } },
        { data: { id: '2', label: '1.2.3.4' } },
        { data: { id: '3', label: 'subdomain.example.com' } },
        { data: { source: '1', target: '2' } },
        { data: { source: '1', target: '3' } },
      ],
      layout: {
        name: 'dagre',
        rankDir: 'TB',
      },
    });

    return () => {
      cy.destroy();
    };
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold glow-text">Graph Explorer</h1>
        <p className="text-gray-400 mt-2">Visualize entity relationships and attack chains</p>
      </div>

      <div className="cyber-card">
        <div ref={containerRef} className="w-full h-[600px] bg-cyber-bg rounded" />
      </div>
    </div>
  );
}
