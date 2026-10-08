// Seat order roughly follows the hemicycle, left to right.
const GROUPS: Record<string, { color: string; order: number }> = {
  GUE_NGL: { color: "#b5374f", order: 1 },
  SD: { color: "#e2524b", order: 2 },
  GREEN_EFA: { color: "#4fae5b", order: 3 },
  RENEW: { color: "#e8b73d", order: 4 },
  EPP: { color: "#5fa8e8", order: 5 },
  ECR: { color: "#3f7fc9", order: 6 },
  PFE: { color: "#8a63c9", order: 7 },
  ESN: { color: "#9c7a54", order: 8 },
  NI: { color: "#8c96a8", order: 9 },
};

export function groupColor(code: string | undefined) {
  return (code && GROUPS[code]?.color) || "#8c96a8";
}

export function groupOrder(code: string | undefined) {
  return GROUPS[code ?? ""]?.order ?? 99;
}

export function byHemicycle<T>(items: T[], code: (item: T) => string | undefined) {
  return [...items].sort(
    (a, b) => (GROUPS[code(a) ?? ""]?.order ?? 99) - (GROUPS[code(b) ?? ""]?.order ?? 99),
  );
}
