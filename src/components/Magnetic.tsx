"use client";

import { useRef, useState } from "react";
import { motion } from "framer-motion";

export default function Magnetic({
  children,
  className = "",
  strength = 30, // Higher number = more movement
}: {
  children: React.ReactNode;
  className?: string;
  strength?: number;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [position, setPosition] = useState({ x: 0, y: 0 });

  const handleMouse = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!ref.current) return;
    const { clientX, clientY } = e;
    const { height, width, left, top } = ref.current.getBoundingClientRect();
    
    // Calculate distance from center of element
    const middleX = clientX - (left + width / 2);
    const middleY = clientY - (top + height / 2);
    
    // Set position within bounds
    setPosition({ x: middleX * (strength / 100), y: middleY * (strength / 100) });
  };

  const reset = () => {
    setPosition({ x: 0, y: 0 });
  };

  return (
    <motion.div
      ref={ref}
      onMouseMove={handleMouse}
      onMouseLeave={reset}
      animate={{ x: position.x, y: position.y }}
      transition={{ type: "spring", stiffness: 150, damping: 15, mass: 0.1 }}
      className={`magnetic ${className}`}
      style={{ display: "inline-block" }}
    >
      {children}
    </motion.div>
  );
}
