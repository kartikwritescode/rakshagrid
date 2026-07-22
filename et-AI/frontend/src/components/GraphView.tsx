import React, { useRef, useEffect, useState } from 'react';

interface Node {
  id: string;
  type: string;
  label: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

interface Link {
  source: string;
  target: string;
}

interface GraphViewProps {
  nodes: Node[];
  links: Link[];
  selectedNodeId?: string | null;
  onNodeSelect?: (nodeId: string | null) => void;
}

export default function GraphView({
  nodes: initialNodes,
  links: initialLinks,
  selectedNodeId = null,
  onNodeSelect
}: GraphViewProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  
  // Store nodes and links in refs to avoid restarting physics on prop updates
  const nodesRef = useRef<Node[]>([]);
  const linksRef = useRef<Link[]>([]);
  
  // Camera transform state
  const [transform, setTransform] = useState({ x: 0, y: 0, k: 1 });
  const transformRef = useRef({ x: 0, y: 0, k: 1 });
  
  // Dragging and interaction state
  const dragNodeRef = useRef<Node | null>(null);
  const hoverNodeRef = useRef<Node | null>(null);
  const isPanningRef = useRef(false);
  const panStartRef = useRef({ x: 0, y: 0 });

  // Node Color Mapper
  const getNodeColor = (type: string, isDimmed: boolean) => {
    if (isDimmed) return 'rgba(51, 65, 85, 0.2)'; // Faded out
    
    switch (type) {
      case 'Victim': return '#6366f1';     // Indigo
      case 'Phone': return '#f97316';      // Orange
      case 'UPI': return '#eab308';        // Yellow
      case 'BankAccount': return '#10b981'; // Emerald
      case 'Device': return '#f43f5e';     // Rose
      default: return '#94a3b8';           // Slate
    }
  };

  // 1. Initialize nodes with random positions if not present
  useEffect(() => {
    const prevNodesMap = new Map(nodesRef.current.map(n => [n.id, n]));
    
    nodesRef.current = initialNodes.map(node => {
      const existing = prevNodesMap.get(node.id);
      return {
        ...node,
        x: existing?.x ?? (Math.random() - 0.5) * 400 + 400,
        y: existing?.y ?? (Math.random() - 0.5) * 400 + 300,
        vx: existing?.vx ?? 0,
        vy: existing?.vy ?? 0
      };
    });
    
    linksRef.current = [...initialLinks];
    
    // Auto-center camera if it's the first load
    if (transformRef.current.x === 0 && transformRef.current.y === 0 && canvasRef.current) {
      const canvas = canvasRef.current;
      transformRef.current = {
        x: canvas.width / 2 - 400,
        y: canvas.height / 2 - 300,
        k: 1
      };
      setTransform({ ...transformRef.current });
    }
  }, [initialNodes, initialLinks]);

  // 2. Physics Simulation & Drawing loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    // Resize handler
    const resizeCanvas = () => {
      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight || 500;
      }
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    // Physics constants
    const repellingForce = 120;
    const springLength = 80;
    const springStrength = 0.04;
    const gravity = 0.015;
    const friction = 0.85;

    const runSimulationStep = () => {
      const nodes = nodesRef.current;
      const links = linksRef.current;

      // 1. Repulsion (between all nodes)
      for (let i = 0; i < nodes.length; i++) {
        const nodeA = nodes[i];
        for (let j = i + 1; j < nodes.length; j++) {
          const nodeB = nodes[j];
          const dx = nodeB.x! - nodeA.x!;
          const dy = nodeB.y! - nodeA.y!;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          
          if (distance < 300) {
            const force = (repellingForce * repellingForce) / distance;
            const fx = (dx / distance) * force;
            const fy = (dy / distance) * force;
            
            // Push apart
            nodeA.vx = (nodeA.vx || 0) - fx * 0.05;
            nodeA.vy = (nodeA.vy || 0) - fy * 0.05;
            nodeB.vx = (nodeB.vx || 0) + fx * 0.05;
            nodeB.vy = (nodeB.vy || 0) + fy * 0.05;
          }
        }
      }

      // 2. Attraction (along link edges)
      const nodeMap = new Map(nodes.map(n => [n.id, n]));
      for (const link of links) {
        const sourceNode = nodeMap.get(link.source);
        const targetNode = nodeMap.get(link.target);
        
        if (sourceNode && targetNode) {
          const dx = targetNode.x! - sourceNode.x!;
          const dy = targetNode.y! - sourceNode.y!;
          const distance = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = (distance - springLength) * springStrength;
          const fx = (dx / distance) * force;
          const fy = (dy / distance) * force;
          
          // Pull together
          sourceNode.vx = (sourceNode.vx || 0) + fx;
          sourceNode.vy = (sourceNode.vy || 0) + fy;
          targetNode.vx = (targetNode.vx || 0) - fx;
          targetNode.vy = (targetNode.vy || 0) - fy;
        }
      }

      // 3. Center Gravity & Apply Positions
      const centerX = 400;
      const centerY = 300;
      for (const node of nodes) {
        // Center force
        node.vx = (node.vx || 0) + (centerX - node.x!) * gravity;
        node.vy = (node.vy || 0) + (centerY - node.y!) * gravity;

        // Apply friction
        node.vx *= friction;
        node.vy *= friction;

        // Update positions (if not dragging)
        if (node !== dragNodeRef.current) {
          node.x! += node.vx;
          node.y! += node.vy;
        }
      }
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      ctx.save();
      // Apply Pan & Zoom
      const t = transformRef.current;
      ctx.translate(t.x, t.y);
      ctx.scale(t.k, t.k);

      const nodes = nodesRef.current;
      const links = linksRef.current;
      const hovered = hoverNodeRef.current;

      // Identify active subgraph if a node is selected or hovered
      const activeId = selectedNodeId || hovered?.id;
      const connectedNodes = new Set<string>();
      if (activeId) {
        connectedNodes.add(activeId);
        for (const link of links) {
          if (link.source === activeId) connectedNodes.add(link.target);
          if (link.target === activeId) connectedNodes.add(link.source);
        }
      }

      // 1. Draw Links
      ctx.lineWidth = 1;
      for (const link of links) {
        const nodeMap = new Map(nodes.map(n => [n.id, n]));
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

      // 2. Draw Nodes
      for (const node of nodes) {
        const isDimmed = activeId !== undefined && activeId !== null && !connectedNodes.has(node.id);
        const isHighlighted = node.id === activeId;
        const color = getNodeColor(node.type, isDimmed);
        
        ctx.beginPath();
        // Node size depending on type
        const radius = node.type === 'Victim' ? 8 : 12;
        ctx.arc(node.x!, node.y!, radius, 0, 2 * Math.PI);
        ctx.fillStyle = color;
        ctx.fill();

        // Node Ring Highlight
        if (isHighlighted) {
          ctx.strokeStyle = '#ffffff';
          ctx.lineWidth = 2.5;
          ctx.stroke();
          
          // Draw outer glow rings
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

        // 3. Draw Labels (Only if zoomed in or node is active/highlighted)
        const shouldShowLabel = t.k > 0.65 || isHighlighted || connectedNodes.has(node.id);
        if (shouldShowLabel) {
          ctx.fillStyle = isDimmed ? 'rgba(148, 163, 184, 0.2)' : '#e2e8f0';
          ctx.font = isHighlighted ? 'bold 11px sans-serif' : '10px sans-serif';
          ctx.textAlign = 'center';
          ctx.fillText(node.label, node.x!, node.y! + radius + 14);
          
          // Show type below name/id for highlighted ones
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
  }, [selectedNodeId]);

  // Coordinate helper
  const getCanvasCoords = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current;
    if (!canvas) return { x: 0, y: 0 };
    const rect = canvas.getBoundingClientRect();
    const clientX = e.clientX - rect.left;
    const clientY = e.clientY - rect.top;
    
    // Transform screen coordinates back to graph canvas space
    const t = transformRef.current;
    return {
      x: (clientX - t.x) / t.k,
      y: (clientY - t.y) / t.k
    };
  };

  // Dragging and Panning Handlers
  const handleMouseDown = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getCanvasCoords(e);
    
    // Check if clicked a node
    let clickedNode: Node | null = null;
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
      if (onNodeSelect) {
        onNodeSelect(clickedNode.id);
      }
    } else {
      // Pan state
      isPanningRef.current = true;
      panStartRef.current = { x: e.clientX - transformRef.current.x, y: e.clientY - transformRef.current.y };
    }
  };

  const handleMouseMove = (e: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getCanvasCoords(e);

    // 1. Handle Node Dragging
    if (dragNodeRef.current) {
      dragNodeRef.current.x = x;
      dragNodeRef.current.y = y;
      dragNodeRef.current.vx = 0;
      dragNodeRef.current.vy = 0;
      return;
    }

    // 2. Handle Panning
    if (isPanningRef.current) {
      const t = transformRef.current;
      t.x = e.clientX - panStartRef.current.x;
      t.y = e.clientY - panStartRef.current.y;
      setTransform({ ...t });
      return;
    }

    // 3. Handle Hover detection
    let hovered: Node | null = null;
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
    hoverNodeRef.current = hovered;
  };

  const handleMouseUp = () => {
    dragNodeRef.current = null;
    isPanningRef.current = false;
  };

  const handleWheel = (e: React.WheelEvent<HTMLCanvasElement>) => {
    e.preventDefault();
    const canvas = canvasRef.current;
    if (!canvas) return;

    const zoomFactor = 1.1;
    const t = transformRef.current;
    
    // Zoom centered on cursor
    const rect = canvas.getBoundingClientRect();
    const mouseX = e.clientX - rect.left;
    const mouseY = e.clientY - rect.top;
    
    const wheel = e.deltaY < 0 ? 1 : -1;
    const k = wheel > 0 ? t.k * zoomFactor : t.k / zoomFactor;
    
    // Constrain scale
    const newK = Math.max(0.15, Math.min(4, k));
    
    // Adjust offsets to zoom on mouse position
    t.x = mouseX - (mouseX - t.x) * (newK / t.k);
    t.y = mouseY - (mouseY - t.y) * (newK / t.k);
    t.k = newK;
    
    setTransform({ ...t });
  };

  const handleResetZoom = () => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    transformRef.current = {
      x: canvas.width / 2 - 400,
      y: canvas.height / 2 - 300,
      k: 0.95
    };
    setTransform({ ...transformRef.current });
    if (onNodeSelect) onNodeSelect(null);
  };

  return (
    <div className="relative w-full h-full min-h-[450px] bg-slate-950 rounded-xl overflow-hidden border border-slate-900">
      {/* Legend overlays */}
      <div className="absolute top-4 left-4 z-10 glass-panel border-slate-800 p-3 rounded-lg text-xs space-y-2 select-none pointer-events-none">
        <h4 className="font-semibold text-slate-300 border-b border-slate-800 pb-1.5 mb-1.5">Network Node Types</h4>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded-full bg-[#6366f1] inline-block"></span>
          <span>Victims</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded-full bg-[#f97316] inline-block"></span>
          <span>Phones</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded-full bg-[#eab308] inline-block"></span>
          <span>UPI handles</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded-full bg-[#10b981] inline-block"></span>
          <span>Bank Accounts</span>
        </div>
        <div className="flex items-center gap-2 text-slate-300">
          <span className="w-3 h-3 rounded-full bg-[#f43f5e] inline-block"></span>
          <span>Devices</span>
        </div>
      </div>

      {/* Control overlays */}
      <div className="absolute bottom-4 right-4 z-10 flex gap-2">
        <button
          onClick={handleResetZoom}
          className="px-3 py-1.5 text-xs bg-slate-900 border border-slate-800 text-slate-300 rounded hover:bg-slate-800 hover:text-white transition-colors"
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
