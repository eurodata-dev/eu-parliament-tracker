import { ImageResponse } from "next/og";
import { getVote } from "@/lib/htv";
import { markDots } from "@/lib/mark";

export const alt = "Vote result";
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

export default async function Image({ params }: { params: Promise<{ id: string }> }) {
  const vote = await getVote((await params).id);
  const t = vote.stats.total;
  const adopted = vote.result === "ADOPTED";
  const title = vote.display_title.length > 120 ? `${vote.display_title.slice(0, 117)}…` : vote.display_title;

  return new ImageResponse(
    (
      <div
        style={{
          width: "100%",
          height: "100%",
          display: "flex",
          flexDirection: "column",
          justifyContent: "space-between",
          padding: 64,
          background: "#0f1b3d",
          color: "#f2f4f9",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", fontSize: 24, color: "#8899bb" }}>
          <span style={{ display: "flex", alignItems: "center", gap: 16, letterSpacing: 5 }}>
            <Mark size={54} />
            EU PARLIAMENT TRACKER
          </span>
          <span>{vote.timestamp.slice(0, 10)}</span>
        </div>
        <div style={{ fontSize: title.length > 70 ? 52 : 64, lineHeight: 1.12 }}>{title}</div>
        <div style={{ display: "flex", flexDirection: "column", gap: 18 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 36, fontSize: 34 }}>
            <span
              style={{
                padding: "6px 16px",
                border: `2px solid ${adopted ? "#2fb36b" : "#e5484d"}`,
                color: adopted ? "#2fb36b" : "#e5484d",
                fontSize: 24,
                letterSpacing: 3,
              }}
            >
              {adopted ? "ADOPTED" : "REJECTED"}
            </span>
            <span style={{ color: "#2fb36b" }}>{t.FOR} for</span>
            <span style={{ color: "#e5484d" }}>{t.AGAINST} against</span>
            <span style={{ color: "#d9a23b" }}>{t.ABSTENTION} abstained</span>
          </div>
          <div style={{ display: "flex", height: 14 }}>
            <div style={{ flex: t.FOR, background: "#2fb36b" }} />
            <div style={{ flex: t.AGAINST, background: "#e5484d" }} />
            <div style={{ flex: t.ABSTENTION, background: "#d9a23b" }} />
          </div>
        </div>
      </div>
    ),
    size,
  );
}
