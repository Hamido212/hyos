"use client";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export default function Typewriter({
  text,
  delay = 0,
  className = "",
}: {
  text: string;
  delay?: number;
  className?: string;
}) {
  const [displayText, setDisplayText] = useState("");
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    
    // Delay before starting
    const startTimeout = setTimeout(() => {
      setIsTyping(true);
      let currentIndex = 0;
      
      timeout = setInterval(() => {
        if (currentIndex <= text.length) {
          setDisplayText(text.slice(0, currentIndex));
          currentIndex++;
        } else {
          clearInterval(timeout);
          setIsTyping(false);
        }
      }, 30); // Typing speed
    }, delay * 1000);

    return () => {
      clearTimeout(startTimeout);
      clearInterval(timeout);
    };
  }, [text, delay]);

  return (
    <span className={className}>
      {displayText}
      {isTyping && (
        <motion.span
          animate={{ opacity: [1, 0] }}
          transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
          className="inline-block w-[0.5em] h-[1em] bg-[#ccff00] ml-1 align-middle"
        />
      )}
    </span>
  );
}
