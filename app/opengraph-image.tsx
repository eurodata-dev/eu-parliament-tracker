import { ImageResponse } from "next/og";
import { markDots } from "@/lib/mark";

export const alt = "EU Parliament Tracker";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

function Mark({ size }: { size: number }) {
  return (
    <svg width={size} height={(size * 14) / 24} viewBox="0 5.5 24 14">
      {markDots().map((d, i) => (
        <circle key={i} cx={d.cx} cy={d.cy} r="1.15" fill={d.fill} />
      ))}
    </svg>
  );
}

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 72,
          background: "#0f1b3d",
          color: "#f2f4f9",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 20, fontSize: 26, letterSpacing: 6, color: "#8899bb" }}>
          <Mark size={64} />
          <span>EU PARLIAMENT TRACKER</span>
        </div>
        <div style={{ display: "flex", flexDirection: "column", fontSize: 76, lineHeight: 1.05 }}>
          <span>Track every vote.</span>
          <span style={{ color: "#8899bb" }}>Understand every decision.</span>
        </div>
        <div style={{ display: "flex", height: 14 }}>
          <div style={{ flex: 395, background: "#2fb36b" }} />
          <div style={{ flex: 136, background: "#e5484d" }} />
          <div style={{ flex: 80, background: "#d9a23b" }} />
        </div>
      </div>
    ),
    size,
  );
}
