import { ImageResponse } from "next/og";
import { seatLayout, seatRadius } from "@/lib/hemicycle";

export const alt = "Who votes like you? EU Parliament Tracker";
export const size = { width: 1200, height: 630 };
export const contentType = "image/png";

const SEATS = seatLayout(720);
const DOT = seatRadius(720);
const COLORS = ["#e5484d", "#d9a23b", "#2fb36b"];

export default function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: 64,
          background: "#0f1b3d",
          color: "#f2f4f9",
        }}
      >
        <div style={{ display: "flex", flexDirection: "column", width: 470 }}>
          <span style={{ fontSize: 22, letterSpacing: 5, color: "#d9a23b" }}>EU PARLIAMENT TRACKER</span>
          <span style={{ marginTop: 28, fontSize: 72, lineHeight: 1.05 }}>Who votes like you?</span>
          <span style={{ marginTop: 24, fontSize: 28, color: "#c9d1e3", lineHeight: 1.4 }}>
            Answer 10 real votes. See which MEPs agree with you, seat by seat.
          </span>
        </div>
        <svg width="600" height="317" viewBox="-1.04 -1.04 2.08 1.1">
          {SEATS.map((p, i) => {
            const n = Math.sin(i * 12.9898) * 43758.5453;
            const r = n - Math.floor(n);
            const lean = p.angle / Math.PI;
            const c = r < 0.15 + lean * 0.5 ? COLORS[2] : r < 0.55 + lean * 0.3 ? COLORS[1] : COLORS[0];
            return <circle key={i} cx={p.x.toFixed(4)} cy={(-p.y).toFixed(4)} r={DOT.toFixed(4)} fill={c} />;
          })}
        </svg>
      </div>
    ),
    size,
  );
}
