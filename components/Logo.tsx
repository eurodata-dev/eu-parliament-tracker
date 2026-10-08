import { markDots } from "@/lib/mark";

const DOTS = markDots({ inner: "var(--muted)", middle: "var(--text)", outer: "var(--abstain)" });

export default function Logo({ size = 22 }: { size?: number }) {
  return (
    <svg width={size} height={Math.round((size * 14) / 24)} viewBox="0 5.5 24 14" aria-hidden="true">
      {DOTS.map((d, i) => (
        <circle key={i} cx={d.cx} cy={d.cy} r="1.15" fill={d.fill} />
      ))}
    </svg>
  );
}
