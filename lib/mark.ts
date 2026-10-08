// logo: 3 rows of seats, 24x24 grid. used by header, favicon and og images
const ROWS = [
  { radius: 5, seats: 7 },
  { radius: 8, seats: 11 },
  { radius: 11, seats: 15 },
] as const;

export const MARK_COLORS = { inner: "#8899bb", middle: "#f2f4f9", outer: "#d9a23b" };

export function markDots(colors: { inner: string; middle: string; outer: string } = MARK_COLORS) {
  const fills = [colors.inner, colors.middle, colors.outer];
  return ROWS.flatMap((row, r) =>
    Array.from({ length: row.seats }, (_, i) => {
      const angle = Math.PI * (1 - i / (row.seats - 1));
      return {
        cx: Number((12 + Math.cos(angle) * row.radius).toFixed(2)),
        cy: Number((18 - Math.sin(angle) * row.radius).toFixed(2)),
        fill: fills[r],
      };
    }),
  );
}
