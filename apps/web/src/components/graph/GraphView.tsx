// apps/web/src/components/graph/GraphView.tsx
import React, { useRef, useEffect, useState, useMemo, useCallback } from 'react';

export interface GraphNode {
  id: string;
  type: string;
  label: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface GraphLink {
  source: string;
  target: string;
  relation?: string;
  weight?: number;
}

export interface GraphViewProps {
  nodes: GraphNode[];
  links: GraphLink[];
  selectedNodeId?: string | null;
  onNodeSelect?: (nodeId: string | null) => void;
  maxNodes?: number;
}

export default function GraphView({
  nodes: initialNodes,
  links: initialLinks,
  selectedNodeId = null,
  onNodeSelect,
  maxNodes = 1000,
}: GraphViewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);

  const nodesRef = useRef<GraphNode[]>([]);
  const linksRef = useRef<GraphLink[]>([]);
  const nodeMapRef = useRef<Map<string, GraphNode>>(new Map());

  // Simulation cooling & stabilization state
  const alphaRef = useRef<number>(1.0);
  const isSimulatingRef = useRef<boolean>(true);
  const isDirtyRef = useRef<boolean>(true);
  const [simulationState, setSimulationState] = useState<'simulating' | 'stabilized'>('simulating');

  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const transformRef = useRef({ x: 0, y: 0, k: 1 });

  const dragNodeRef = useRef<GraphNode | null>(null);
  const hoverNodeRef = useRef<GraphNode | null>(null);
  const isPanningRef = useRef(false);
  const panStartRef = useRef({ x: 0, y: 0 });

  // Limit dataset size for performance if necessary
  const cappedNodes = useMemo(() => {
    return initialNodes.slice(0, maxNodes);
  }, [initialNodes, maxNodes]);

  const cappedLinks = useMemo(() => {
    const nodeIds = new Set(cappedNodes.map(n => n.id));
    return initialLinks.filter(l => nodeIds.has(l.source) && nodeIds.has(l.target));
  }, [cappedNodes, initialLinks]);

  const getNodeColor = useCallback((type: string, isDimmed: boolean) => {
    if (isDimmed) return 'rgba(51, 65, 85, 0.2)';
    switch (type) {
      case 'Victim': return '#6366f1';
      case 'Phone': return '#f97316';
      case 'UPI': return '#eab308';
      case 'BankAccount': return '#10b981';
      case 'Device': return '#f43f5e';
      default: return '#94a3b8';
    }
  }, []);

  // Initialize or update nodes with position persistence and clustering
  useEffect(() => {
    const prevMap = nodeMapRef.current;
    const newNodes = cappedNodes.map((node, i) => {
      const existing = prevMap.get(node.id);
      if (existing && existing.x !== undefined && existing.y !== undefined) {
        return {
          ...node,
          x: existing.x,
          y: existing.y,
          vx: existing.vx || 0,
          vy: existing.vy || 0,
        };
      }
      // Distribute in a spiral or circular layout
      const angle = (i / Math.max(cappedNodes.length, 1)) * 2 * Math.PI * 3;
      const radius = 60 + Math.sqrt(i) * 35;
      return {
        ...node,
        x: 400 + Math.cos(angle) * radius + (Math.random() - 0.5) * 40,
        y: 300 + Math.sin(angle) * radius + (Math.random() - 0.5) * 40,
        vx: 0,
        vy: 0,
      };
    });

    nodesRef.current = newNodes;
    linksRef.current = [...cappedLinks];
    nodeMapRef.current = new Map(newNodes.map(n => [n.id, n]));

    // Re-heat simulation on data change
    alphaRef.current = 1.0;
    isSimulatingRef.current = true;
    isDirtyRef.current = true;
    setSimulationState('simulating');

    if (transformRef.current.x === 0 && transformRef.current.y === 0 && canvasRef.current) {
      const canvas = canvasRef.current;
      transformRef.current = {
        x: canvas.width / 2 - 400,
        y: canvas.height / 2 - 300,
        k: cappedNodes.length > 300 ? 0.6 : 0.9,
      };
      setTransform({ ...transformRef.current });
    }
  }, [cappedNodes, cappedLinks]);

  // Main Canvas & Simulation Loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight || 500;
        isDirtyRef.current = true;
      }
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Optimized Force Layout with Spatial Grid Partitioning
    const repellingForce = 100;
    const springLength = 80;
    const springStrength = 0.04;
    const gravity = 0.015;
    const friction = 0.82;
    const alphaDecay = 0.985;
    const minAlpha = 0.005;
    const cellSize = 180; // Spatial hashing cell size for O(N) neighbor lookups

    const runSimulationStep = () => {
      if (!isSimulatingRef.current) return;

      const alpha = alphaRef.current;
      if (alpha < minAlpha) {
        isSimulatingRef.current = false;
        setSimulationState('stabilized');
        return;
      }

      const nodes = nodesRef.current;
      const links = linksRef.current;
      const nodeCount = nodes.length;

      // 1. Spatial Grid Bucketing for Repulsion (O(N) instead of O(N²))
      const grid = new Map<string, GraphNode[]>();
      for (let i = 0; i < nodeCount; i++) {
        const node = nodes[i];
        const cx = Math.floor(node.x! / cellSize);
        const cy = Math.floor(node.y! / cellSize);
        const key = `${cx},${cy}`;
        let cell = grid.get(key);
        if (!cell) {
          cell = [];
          grid.set(key, cell);
        }
        cell.push(node);
      }

      // Repulsion between nodes in same and adjacent cells
      for (let i = 0; i < nodeCount; i++) {
        const nodeA = nodes[i];
        const cx = Math.floor(nodeA.x! / cellSize);
        const cy = Math.floor(nodeA.y! / cellSize);

        for (let ox = -1; ox <= 1; ox++) {
          for (let oy = -1; oy <= 1; oy++) {
            const neighborKey = `${cx + ox},${cy + oy}`;
            const cell = grid.get(neighborKey);
            if (!cell) continue;

            for (let j = 0; j < cell.length; j++) {
              const nodeB = cell[j];
              if (nodeA.id >= nodeB.id) continue; // Unique unordered pairs

              const dx = nodeB.x! - nodeA.x!;
              const dy = nodeB.y! - nodeA.y!;
              const distSq = dx * dx + dy * dy;

              if (distSq > 0 && distSq < cellSize * cellSize) {
                const distance = Math.sqrt(distSq) || 1;
                const force = ((repellingForce * repellingForce) / distance) * alpha;
                const fx = (dx / distance) * force * 0.04;
                const fy = (dy / distance) * force * 0.04;

                nodeA.vx = (nodeA.vx || 0) - fx;
                nodeA.vy = (nodeA.vy || 0) - fy;
                nodeB.vx = (nodeB.vx || 0) + fx;
                nodeB.vy = (nodeB.vy || 0) + fy;
              }
            }
          }
        }
      }

      // 2. Spring Link Attraction
      const nodeMap = nodeMapRef.current;
      for (let i = 0; i < links.length; i++) {
        const link = links[i];
        const sourceNode = nodeMap.get(link.source);
        const targetNode = nodeMap.get(link.target);

        if (sourceNode && targetNode) {
          const dx = targetNode.x! - sourceNode.x!;
          const dy = targetNode.y! - sourceNode.y!;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = (distance - springLength) * springStrength * alpha;
          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;

          sourceNode.vx = (sourceNode.vx || 0) + fx;
          sourceNode.vy = (sourceNode.vy || 0) + fy;
          targetNode.vx = (targetNode.vx || 0) - fx;
          targetNode.vy = (targetNode.vy || 0) - fy;
        }
      }

      // 3. Gravity, Friction, and Velocity Integration
      const centerX = 400;
      const centerY = 300;
      let maxVelocity = 0;

      for (let i = 0; i < nodeCount; i++) {
        const node = nodes[i];
        node.vx = (node.vx || 0) + (centerX - node.x!) * gravity * alpha;
        node.vy = (node.vy || 0) + (centerY - node.y!) * gravity * alpha;

        node.vx *= friction;
        node.vy *= friction;

        const vel = Math.abs(node.vx) + Math.abs(node.vy);
        if (vel > maxVelocity) maxVelocity = vel;

        if (node !== dragNodeRef.current) {
          node.x! += node.vx;
          node.y! += node.vy;
        }
      }

      // Decay simulation energy (cooling)
      alphaRef.current *= alphaDecay;
      if (maxVelocity < 0.04 && alphaRef.current < 0.05) {
        alphaRef.current = 0;
        isSimulatingRef.current = false;
        setSimulationState('stabilized');
      }

      isDirtyRef.current = true;
    };

    // Render pass
    const draw = () => {
      if (!isDirtyRef.current && !isSimulatingRef.current) return;
      isDirtyRef.current = false;

      ctx.clearRect(0, 0, canvas.width, canvas.height);

      ctx.save();
      const t = transformRef.current;
      ctx.translate(t.x, t.y);
      ctx.scale(t.k, t.k);

      const nodes = nodesRef.current;
      const links = linksRef.current;
      const hovered = hoverNodeRef.current;
      const nodeMap = nodeMapRef.current;

      const activeId = selectedNodeId || hovered?.id;
      const connectedNodes = new Set<string>();

      if (activeId) {
        connectedNodes.add(activeId);
        for (let i = 0; i < links.length; i++) {
          const link = links[i];
          if (link.source === activeId) connectedNodes.add(link.target);
          if (link.target === activeId) connectedNodes.add(link.source);
        }
      }

      // Draw Edges
      for (let i = 0; i < links.length; i++) {
        const link = links[i];
        const sourceNode = nodeMap.get(link.source);
        const targetNode = nodeMap.get(link.target);

        if (sourceNode && targetNode) {
          const isDimmed = activeId !== undefined && activeId !== null &&
            (!connectedNodes.has(link.source) || !connectedNodes.has(link.target));

          ctx.strokeStyle = isDimmed ? 'rgba(51, 65, 85, 0.05)' : 'rgba(99, 102, 241, 0.25)';
          ctx.lineWidth = isDimmed ? 0.5 : 1.5;
          ctx.beginPath();
          ctx.moveTo(sourceNode.x!, sourceNode.y!);
          ctx.lineTo(targetNode.x!, targetNode.y!);
          ctx.stroke();
        }
      }

      // Draw Nodes
      const nodeCount = nodes.length;
      for (let i = 0; i < nodeCount; i++) {
        const node = nodes[i];
        const isDimmed = activeId !== undefined && activeId !== null && !connectedNodes.has(node.id);
        const isHighlighted = node.id === activeId;
        const color = getNodeColor(node.type, isDimmed);

        ctx.beginPath();
        const radius = node.type === 'Victim' ? 8 : 12;
        ctx.arc(node.x!, node.y!, radius, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();

        if (isHighlighted) {
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 2.5;
          ctx.stroke();

          ctx.strokeStyle = 'rgba(99, 102, 241, 0.4)';
          ctx.lineWidth = 4;
          ctx.beginPath();
          ctx.arc(node.x!, node.y!, radius + 4, 0, 2 * Math.PI);
          ctx.stroke();
        } else if (connectedNodes.has(node.id)) {
          ctx.strokeStyle = 'rgba(255, 255, 255, 0.6)';
          ctx.lineWidth = 1.5;
          ctx.stroke();
        }

        const shouldShowLabel = t.k > 0.65 || isHighlighted || connectedNodes.has(node.id);
        if (shouldShowLabel && (!isDimmed || isHighlighted)) {
          ctx.fillStyle = isDimmed ? 'rgba(148, 163, 184, 0.2)' : '#e2e8f0';
          ctx.font = isHighlighted ? 'bold 11px sans-serif' : '10px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(node.label, node.x!, node.y! + radius + 14);

          if (isHighlighted) {
            ctx.fillStyle = '#94a3b8';
            ctx.font = '9px sans-serif';
            ctx.fillText(node.type.toUpperCase(), node.x!, node.y! + radius + 25);
          }
        }
      }

      ctx.restore();
    };

    const loop = () => {
      runSimulationStep();
      draw();
      animationRef.current = requestAnimationFrame(loop);
    };

    loop();

    return () => {
      window.removeEventListener('resize', resizeCanvas);
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [getNodeColor, selectedNodeId]);

  // Re-heat simulation when user interacts or requests
  const reheatSimulation = useCallback(() => {
    alphaRef.current = 0.5;
    isSimulatingRef.current = true;
    isDirtyRef.current = true;
    setSimulationState('simulating');
  }, []);

  const getCanvasCoords = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const clientY = e.clientY - rect.top;

    const t = transformRef.current;
    return {
      x: (clientX - t.x) / t.k,
      y: (clientY - t.y) / t.k,
    };
  };

  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getCanvasCoords(e);

    let clickedNode: GraphNode | null = null;
    const nodes = nodesRef.current;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const node = nodes[i];
      const radius = node.type === 'Victim' ? 8 : 12;
      const dx = node.x! - x;
      const dy = node.y! - y;
      if (dx * dx + dy * dy < radius * radius * 1.5) {
        clickedNode = node;
        break;
      }
    }

    if (clickedNode) {
      dragNodeRef.current = clickedNode;
      reheatSimulation();
      if (onNodeSelect) {
        onNodeSelect(clickedNode.id);
      }
    } else {
      isPanningRef.current = true;
      panStartRef.current = { x: e.clientX - transformRef.current.x, y: e.clientY - transformRef.current.y };
    }
    isDirtyRef.current = true;
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getCanvasCoords(e);

    if (dragNodeRef.current) {
      dragNodeRef.current.x = x;
      dragNodeRef.current.y = y;
      dragNodeRef.current.vx = 0;
      dragNodeRef.current.vy = 0;
      isDirtyRef.current = true;
      return;
    }

    if (isPanningRef.current) {
      const t = transformRef.current;
      t.x = e.clientX - panStartRef.current.x;
      t.y = e.clientY - panStartRef.current.y;
      setTransform({ ...t });
      isDirtyRef.current = true;
      return;
    }

    let hovered: GraphNode | null = null;
    const nodes = nodesRef.current;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const node = nodes[i];
      const radius = node.type === 'Victim' ? 8 : 12;
      const dx = node.x! - x;
      const dy = node.y! - y;
      if (dx * dx + dy * dy < radius * radius * 1.5) {
        hovered = node;
        break;
      }
    }

    if (hoverNodeRef.current !== hovered) {
      hoverNodeRef.current = hovered;
      isDirtyRef.current = true;
    }
  };

  const handleMouseUp = () => {
    dragNodeRef.current = null;
    isPanningRef.current = false;
    isDirtyRef.current = true;
  };

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    if (!canvas) return;

    const zoomFactor = 1.1;
    const t = transformRef.current;

    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;

    const wheel = e.deltaY < 0 ? 1 : -1;
    const k = wheel > 0 ? t.k * zoomFactor : t.k / zoomFactor;
    const newK = Math.max(0.15, Math.min(4, k));

    t.x = mouseX - (mouseX - t.x) * (newK / t.k);
    t.y = mouseY - (mouseY - t.y) * (newK / t.k);
    t.k = newK;

    setTransform({ ...t });
    isDirtyRef.current = true;
  };

  const handleResetZoom = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    transformRef.current = {
      x: canvas.width / 2 - 400,
      y: canvas.height / 2 - 300,
      k: cappedNodes.length > 300 ? 0.6 : 0.95,
    };
    setTransform({ ...transformRef.current });
    isDirtyRef.current = true;
    if (onNodeSelect) onNodeSelect(null);
  };

  return (
    <div className="relative w-full h-full min-h-[450px] bg-slate-950 rounded-xl overflow-hidden border border-slate-900">
      {/* Legend */}
      <div className="absolute top-4 left-4 z-10 glass-panel border-slate-800 p-3 rounded-lg text-xs space-y-1.5 select-none pointer-events-none">
        <h4 className="font-semibold text-slate-300 border-b border-slate-800 pb-1.5 mb-1.5 text-[11px]">
          Entity Node Types
        </h4>
        <div className="flex items-center gap-2 text-slate-300 text-[10px]">
          <span className="w-2.5 h-2.5 rounded-full bg-[#6366f1] inline-block"></span>
          <span>Victims</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300 text-[10px]">
          <span className="w-2.5 h-2.5 rounded-full bg-[#f97316] inline-block"></span>
          <span>Phones</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300 text-[10px]">
          <span className="w-2.5 h-2.5 rounded-full bg-[#eab308] inline-block"></span>
          <span>UPI handles</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300 text-[10px]">
          <span className="w-2.5 h-2.5 rounded-full bg-[#10b981] inline-block"></span>
          <span>Bank Accounts</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300 text-[10px]">
          <span className="w-2.5 h-2.5 rounded-full bg-[#f43f5e] inline-block"></span>
          <span>Devices</span>
        </div>
      </div>

      {/* Status & Control HUD */}
      <div className="absolute top-4 right-4 z-10 flex items-center gap-2 text-xs font-mono">
        <span className={`px-2.5 py-1 rounded-full text-[10px] font-bold border ${
          simulationState === 'stabilized'
            ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
            : 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30 animate-pulse'
        }`}>
          {simulationState === 'stabilized' ? '● STABILIZED' : '⚡ SIMULATING'}
        </span>
        <span className="px-2.5 py-1 rounded-full bg-slate-900 border border-slate-800 text-slate-400 text-[10px]">
          {cappedNodes.length} nodes · {cappedLinks.length} links
        </span>
      </div>

      {/* Action Controls */}
      <div className="absolute bottom-4 right-4 z-10 flex gap-2">
        <button
          onClick={reheatSimulation}
          className="px-3 py-1.5 text-xs bg-slate-900/90 border border-slate-800 text-slate-300 rounded hover:bg-slate-800 hover:text-white transition-colors font-mono"
          title="Re-run physics simulation layout"
        >
          Re-heat Physics
        </button>
        <button
          onClick={handleResetZoom}
          className="px-3 py-1.5 text-xs bg-slate-900/90 border border-slate-800 text-slate-300 rounded hover:bg-slate-800 hover:text-white transition-colors font-mono"
        >
          Reset View
        </button>
      </div>

      <canvas
        ref={canvasRef}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        onWheel={handleWheel}
        className="w-full h-full cursor-grab active:cursor-grabbing block"
      />
    </div>
  );
}
