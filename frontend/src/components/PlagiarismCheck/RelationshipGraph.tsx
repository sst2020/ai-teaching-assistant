import React, { useMemo } from 'react';
import { SimilarityMatrix, SubmissionComparison } from '../../types/plagiarism';

interface RelationshipGraphProps {
  matrix: SimilarityMatrix;
  suspiciousPairs: SubmissionComparison[];
  onNodeClick?: (studentId: string) => void;
}

interface Node {
  id: string;
  name: string;
  x: number;
  y: number;
  connections: number;
  maxSimilarity: number;
}

interface Edge {
  source: string;
  target: string;
  similarity: number;
}

const RelationshipGraph: React.FC<RelationshipGraphProps> = ({
  matrix,
  suspiciousPairs,
  onNodeClick,
}) => {
  const { nodes, edges } = useMemo(() => {
    const n = matrix.student_ids.length;
    const centerX = 200;
    const centerY = 200;
    const radius = 150;

    // 创建节点，按圆形排列
    const nodeList: Node[] = matrix.student_ids.map((id, index) => {
      const angle = (2 * Math.PI * index) / n - Math.PI / 2;
      const connections = suspiciousPairs.filter(
        p => p.student_id_1 === id || p.student_id_2 === id
      ).length;
      
      const similarities = matrix.matrix[index].filter((_, j) => j !== index);
      const maxSim = Math.max(...similarities, 0);

      return {
        id,
        name: matrix.student_names[index] || id,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle),
        connections,
        maxSimilarity: maxSim,
      };
    });

    // 创建边（只显示超过阈值的）
    const edgeList: Edge[] = suspiciousPairs.map(pair => ({
      source: pair.student_id_1,
      target: pair.student_id_2,
      similarity: pair.similarity_score,
    }));

    return { nodes: nodeList, edges: edgeList };
  }, [matrix, suspiciousPairs]);

  const getNodeColor = (node: Node): string => {
    if (node.maxSimilarity >= 0.9) return '#dc2626';
    if (node.maxSimilarity >= 0.7) return '#f97316';
    if (node.connections > 0) return '#eab308';
    return '#22c55e';
  };

  const getEdgeColor = (similarity: number): string => {
    if (similarity >= 0.9) return '#dc2626';
    if (similarity >= 0.8) return '#f97316';
    return '#eab308';
  };

  const getNodeById = (id: string): Node | undefined => {
    return nodes.find(n => n.id === id);
  };

  return (
    <div className="relationship-graph">
      <div className="graph-header">
        <h3>🔗 学生相似度关系图</h3>
        <p className="graph-hint">节点大小表示可疑连接数，颜色表示最高相似度</p>
      </div>

      <svg viewBox="0 0 400 400" className="graph-svg">
        {/* 绘制边 */}
        {edges.map((edge, index) => {
          const source = getNodeById(edge.source);
          const target = getNodeById(edge.target);
          if (!source || !target) return null;

          return (
            <line
              key={`edge-${index}`}
              x1={source.x}
              y1={source.y}
              x2={target.x}
              y2={target.y}
              stroke={getEdgeColor(edge.similarity)}
              strokeWidth={Math.max(1, edge.similarity * 4)}
              strokeOpacity={0.6}
            />
          );
        })}

        {/* 绘制节点 */}
        {nodes.map((node) => {
          const nodeRadius = 15 + node.connections * 5;
          
          return (
            <g
              key={node.id}
              className="graph-node"
              onClick={() => onNodeClick?.(node.id)}
              style={{ cursor: 'pointer' }}
            >
              <circle
                cx={node.x}
                cy={node.y}
                r={nodeRadius}
                fill={getNodeColor(node)}
                stroke="#fff"
                strokeWidth={2}
              />
              <text
                x={node.x}
                y={node.y + nodeRadius + 15}
                textAnchor="middle"
                fontSize="10"
                fill="#374151"
              >
                {node.name.slice(0, 6)}
              </text>
              {node.connections > 0 && (
                <text
                  x={node.x}
                  y={node.y + 4}
                  textAnchor="middle"
                  fontSize="10"
                  fill="#fff"
                  fontWeight="bold"
                >
                  {node.connections}
                </text>
              )}
            </g>
          );
        })}
      </svg>

      {/* 统计信息 */}
      <div className="graph-stats">
        <div className="stat-item">
          <span className="stat-label">总学生数</span>
          <span className="stat-value">{nodes.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">可疑连接</span>
          <span className="stat-value flagged">{edges.length}</span>
        </div>
        <div className="stat-item">
          <span className="stat-label">涉及学生</span>
          <span className="stat-value">
            {nodes.filter(n => n.connections > 0).length}
          </span>
        </div>
      </div>
    </div>
  );
};

export default RelationshipGraph;

