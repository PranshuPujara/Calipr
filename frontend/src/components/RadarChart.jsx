import React, { useRef, useEffect } from 'react';

const RadarChart = ({ scores, width = 320, height = 320 }) => {
  const canvasRef = useRef(null);
  const animationRef = useRef(null);
  const currentValuesRef = useRef([0, 0, 0, 0, 0]);

  // Map scores dict into ordered array: [semantic, skills, trajectory, behavioral, domain]
  const getTargetValues = (s) => {
    if (!s) return [0, 0, 0, 0, 0];
    return [
      s.semantic ?? 0,
      s.skills ?? 0,
      s.trajectory ?? 0,
      s.behavioral ?? 0,
      s.domain ?? 0
    ];
  };

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const dpr = window.devicePixelRatio || 1;
    
    // Set display size
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    
    // Scale for high DPI
    canvas.width = width * dpr;
    canvas.height = height * dpr;
    ctx.scale(dpr, dpr);

    const config = {
      labels: ["Semantic Fit", "Skills Match", "Trajectory", "Behavioral", "Domain"],
      axesCount: 5,
      centerX: width / 2,
      centerY: height / 2,
      radius: Math.min(width, height) * 0.36,
      animationDuration: 400, // ms
      colors: {
        grid: '#e4e2e2',
        gridText: '#757170',
        axis: '#e4e2e2',
        polygonBorder: '#156cc2',
        polygonFill: 'rgba(132, 185, 239, 0.35)',
        dots: '#156cc2'
      }
    };

    const targetValues = getTargetValues(scores);
    const startValues = [...currentValuesRef.current];
    let startTime = null;

    const draw = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const elapsed = timestamp - startTime;
      const progress = Math.min(elapsed / config.animationDuration, 1);
      
      // Easing out cubic
      const easeProgress = 1 - Math.pow(1 - progress, 3);

      // Interpolate values
      const displayedValues = startValues.map((startVal, i) => {
        const target = targetValues[i];
        return startVal + (target - startVal) * easeProgress;
      });

      // Update ref so we transition smoothly next time
      currentValuesRef.current = [...displayedValues];

      ctx.clearRect(0, 0, width, height);

      // 1. Draw grid rings & ring values
      const ringCount = 5;
      for (let r = 1; r <= ringCount; r++) {
        const ringRadius = (r / ringCount) * config.radius;
        ctx.beginPath();
        for (let i = 0; i < config.axesCount; i++) {
          const angle = (i * 2 * Math.PI / config.axesCount) - (Math.PI / 2);
          const x = config.centerX + ringRadius * Math.cos(angle);
          const y = config.centerY + ringRadius * Math.sin(angle);
          if (i === 0) {
            ctx.moveTo(x, y);
          } else {
            ctx.lineTo(x, y);
          }
        }
        ctx.closePath();
        ctx.strokeStyle = config.colors.grid;
        ctx.lineWidth = 1;
        ctx.stroke();

        // Label values (0.2, 0.4...)
        ctx.fillStyle = config.colors.gridText;
        ctx.font = '10px "Fragment Mono", monospace';
        ctx.textAlign = 'left';
        ctx.fillText((r / ringCount).toFixed(1), config.centerX + 6, config.centerY - ringRadius + 3);
      }

      // 2. Draw axes lines and labels
      for (let i = 0; i < config.axesCount; i++) {
        const angle = (i * 2 * Math.PI / config.axesCount) - (Math.PI / 2);
        
        // Line
        const outerX = config.centerX + config.radius * Math.cos(angle);
        const outerY = config.centerY + config.radius * Math.sin(angle);
        ctx.beginPath();
        ctx.moveTo(config.centerX, config.centerY);
        ctx.lineTo(outerX, outerY);
        ctx.strokeStyle = config.colors.axis;
        ctx.stroke();

        // Label text positioning
        const labelDistance = config.radius + 16;
        const labelX = config.centerX + labelDistance * Math.cos(angle);
        const labelY = config.centerY + labelDistance * Math.sin(angle);
        
        ctx.fillStyle = '#1a1615';
        ctx.font = 'bold 11px "Inter", sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        
        const cos = Math.cos(angle);
        if (Math.abs(cos) < 0.1) {
          ctx.textAlign = 'center';
        } else if (cos > 0) {
          ctx.textAlign = 'left';
        } else {
          ctx.textAlign = 'right';
        }

        ctx.fillText(config.labels[i], labelX, labelY);
      }

      // 3. Draw candidate scores polygon
      ctx.beginPath();
      for (let i = 0; i < config.axesCount; i++) {
        const angle = (i * 2 * Math.PI / config.axesCount) - (Math.PI / 2);
        const valRadius = Math.max(0, Math.min(1, displayedValues[i])) * config.radius;
        const x = config.centerX + valRadius * Math.cos(angle);
        const y = config.centerY + valRadius * Math.sin(angle);
        if (i === 0) {
          ctx.moveTo(x, y);
        } else {
          ctx.lineTo(x, y);
        }
      }
      ctx.closePath();
      ctx.fillStyle = config.colors.polygonFill;
      ctx.fill();
      ctx.strokeStyle = config.colors.polygonBorder;
      ctx.lineWidth = 2;
      ctx.stroke();

      // 4. Draw dots at vertices
      for (let i = 0; i < config.axesCount; i++) {
        const angle = (i * 2 * Math.PI / config.axesCount) - (Math.PI / 2);
        const valRadius = Math.max(0, Math.min(1, displayedValues[i])) * config.radius;
        const x = config.centerX + valRadius * Math.cos(angle);
        const y = config.centerY + valRadius * Math.sin(angle);

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, 2 * Math.PI);
        ctx.fillStyle = config.colors.dots;
        ctx.fill();
        ctx.strokeStyle = '#ffffff';
        ctx.lineWidth = 1.5;
        ctx.stroke();
      }

      if (progress < 1) {
        animationRef.current = requestAnimationFrame(draw);
      }
    };

    animationRef.current = requestAnimationFrame(draw);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [scores, width, height]);

  return (
    <div className="radar-wrapper" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <canvas ref={canvasRef} />
    </div>
  );
};

export default RadarChart;
