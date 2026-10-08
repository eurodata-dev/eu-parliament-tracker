const ROWS = 14;
const INNER = 0.38;

export interface Seat {
  x: number;
  y: number;
  angle: number;
  r: number;
}

// 14 rows, more seats on outer rows. sorted left -> right so groups fill wedges
export function seatLayout(n: number): Seat[] {
  const radii = Array.from({ length: ROWS }, (_, i) => INNER + ((1 - INNER) * i) / (ROWS - 1));
  const sum = radii.reduce((a, b) => a + b, 0);
  const perRow = radii.map((r) => Math.round((n * r) / sum));
  perRow[ROWS - 1] += n - perRow.reduce((a, b) => a + b, 0);

  const points: Seat[] = [];
  radii.forEach((r, row) => {
    const count = perRow[row];
    for (let j = 0; j < count; j++) {
      const angle = count === 1 ? Math.PI / 2 : Math.PI - (j * Math.PI) / (count - 1);
      points.push({ x: r * Math.cos(angle), y: r * Math.sin(angle), angle, r });
    }
  });
  return points.sort((a, b) => b.angle - a.angle || a.r - b.r);
}

export function seatRadius(n: number) {
  return (Math.PI / (n / 9.5)) * 0.36;
}
