import React from "react";
import { useScrollReveal } from "../hooks/useScrollReveal";

type MotionRevealProps = {
  children: React.ReactNode;
  className?: string;
};

export default function MotionReveal({ children, className = "" }: MotionRevealProps) {
  const { ref, visible } = useScrollReveal<HTMLDivElement>();
  const cn = `motion-reveal${visible ? " is-visible" : ""}${className ? ` ${className}` : ""}`.trim();
  return (
    <div ref={ref} className={cn}>
      {children}
    </div>
  );
}
