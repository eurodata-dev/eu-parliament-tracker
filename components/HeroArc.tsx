// deterministic (no Math.random) otherwise hydration mismatch
const ROWS = 9;
const INNER = 0.42;

const dots = (() => {
  const out: { x: number; y: number; c: string }[] = [];
  for (let row = 0; row < ROWS; row++) {
    const r = INNER + ((1 - INNER) * row) / (ROWS - 1);
    const count = Math.round(18 + r * 34);
    for (let j = 0; j < count; j++) {
      const a = Math.PI - (j * Math.PI) / (count - 1);
      const k = (row * 7 + j * 3) % 23;
      const c = k === 0 ? "var(--against)" : k === 5 || k === 11 ? "var(--for)" : k === 17 ? "var(--abstain)" : "var(--line)";
      out.push({ x: r * Math.cos(a), y: -r * Math.sin(a), c });
    }
  }
  return out;
})();

export default function HeroArc({ className }: { className?: string }) {
  return (
    <svg viewBox="-1.05 -1.05 2.1 1.1" className={className} aria-hidden="true">
      {dots.map((d, i) => (
        <circle key={i} cx={d.x.toFixed(3)} cy={d.y.toFixed(3)} r="0.022" fill={d.c} />
      ))}
    </svg>
  );
}
