import { useEffect, useState, useCallback } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Position,
} from 'reactflow';
import { Share2, Loader2 } from 'lucide-react';
import { topicApi } from '@/api/client';
import type { KnowledgeGraphNode, KnowledgeGraphEdge } from '@/types';
import 'reactflow/dist/style.css';

const nodeColors = [
  '#3b82f6', // blue-500
  '#10b981', // emerald-500
  '#f59e0b', // amber-500
  '#ef4444', // red-500
  '#8b5cf6', // violet-500
  '#ec4899', // pink-500
  '#06b6d4', // cyan-500
];

interface FlowNode extends Node {
  data: {
    label: string;
    level: number;
    difficulty: number;
  };
}

interface FlowEdge extends Edge {
  animated?: boolean;
}

export default function KnowledgeGraph() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedNode, setSelectedNode] = useState<KnowledgeGraphNode | null>(null);

  const loadGraph = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await topicApi.getGraph();
      
      const flowNodes: FlowNode[] = data.nodes.map((node) => ({
        id: node.id,
        position: { x: node.x * 300, y: node.y * 150 },
        data: { 
          label: node.name, 
          level: node.level,
          difficulty: node.difficulty,
        },
        style: {
          background: nodeColors[node.level % nodeColors.length],
          color: 'white',
          border: '2px solid white',
          borderRadius: '8px',
          padding: '10px 16px',
          fontSize: '14px',
          fontWeight: 600,
          boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)',
        },
        sourcePosition: Position.Bottom,
        targetPosition: Position.Top,
      }));

      const flowEdges: FlowEdge[] = data.edges.map((edge) => ({
        id: `${edge.source}-${edge.target}`,
        source: edge.source,
        target: edge.target,
        animated: true,
        style: { stroke: '#94a3b8', strokeWidth: 2 },
      }));

      setNodes(flowNodes);
      setEdges(flowEdges);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load knowledge graph');
    } finally {
      setIsLoading(false);
    }
  }, [setNodes, setEdges]);

  useEffect(() => {
    loadGraph();
  }, [loadGraph]);

  const onNodeClick = (_: React.MouseEvent, node: Node) => {
    const nodeData = nodes.find((n) => n.id === node.id);
    if (nodeData) {
      setSelectedNode({
        id: nodeData.id,
        name: nodeData.data.label,
        level: nodeData.data.level,
        difficulty: nodeData.data.difficulty,
        x: nodeData.position.x / 300,
        y: nodeData.position.y / 150,
      });
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <Loader2 className="w-8 h-8 animate-spin text-primary-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="text-red-600">{error}</div>
        <button onClick={loadGraph} className="btn-primary mt-4">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="h-[calc(100vh-8rem)] flex gap-6">
      <div className="flex-1 card p-0 overflow-hidden">
        <div className="p-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Share2 className="w-5 h-5 text-primary-600" />
            <h2 className="text-lg font-semibold text-gray-900">Knowledge Graph</h2>
          </div>
          <div className="text-sm text-gray-500">
            {nodes.length} topics • {edges.length} connections
          </div>
        </div>
        
        <div className="h-[calc(100%-4rem)]">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onNodeClick={onNodeClick}
            fitView
            attributionPosition="bottom-right"
          >
            <Background color="#cbd5e1" gap={16} />
            <Controls />
            <MiniMap 
              nodeStrokeColor={(n) => {
                if (n.style?.background) return String(n.style.background);
                return '#3b82f6';
              }}
              nodeColor={(n) => {
                if (n.style?.background) return String(n.style.background);
                return '#3b82f6';
              }}
            />
          </ReactFlow>
        </div>
      </div>

      {selectedNode && (
        <div className="w-80 card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            {selectedNode.name}
          </h3>
          <div className="space-y-4">
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Level</div>
              <div className="text-lg font-medium text-gray-900">
                {selectedNode.level}
              </div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Difficulty</div>
              <div className="text-lg font-medium text-gray-900">
                {selectedNode.difficulty.toFixed(2)}
              </div>
            </div>
            <div className="p-3 bg-gray-50 rounded-lg">
              <div className="text-sm text-gray-600">Prerequisites</div>
              <div className="text-sm text-gray-700 mt-1">
                {edges
                  .filter((e) => e.target === selectedNode.id)
                  .map((e) => {
                    const node = nodes.find((n) => n.id === e.source);
                    return node?.data.label;
                  })
                  .filter(Boolean)
                  .join(', ') || 'None'}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
