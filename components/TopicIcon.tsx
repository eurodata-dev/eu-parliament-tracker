const PATHS: Record<string, string> = {
  biodiversity: "M12 21V11M12 11C12 6 8 4 4 4c0 4 2 7 8 7Zm0 3c0-4 3-6 8-6 0 4-3 6-8 6",
  "climate-and-environment": "M4 20c0-8 6-14 16-16-1 10-7 16-16 16Zm0 0 8-8",
  "climate-change": "M10 14V5a2 2 0 1 1 4 0v9a4 4 0 1 1-4 0ZM12 9v8M18 6h3M18 10h3",
  "consumer-protection": "M5 8h14l-1.5 12h-11L5 8Zm4 0V6a3 3 0 0 1 6 0v2M9.5 14l2 2 3.5-4",
  digital: "M3 5h18v11H3zM8 20h8M12 16v4",
  "economy-and-budget": "M4 20V10M10 20V4M16 20v-7M22 20H2",
  "education-youth-and-culture": "M2 9l10-5 10 5-10 5-10-5Zm4 2v5c3 2.5 9 2.5 12 0v-5",
  energy: "M13 2 5 13h6l-1 9 8-11h-6l1-9Z",
  enlargement: "M12 8v8M8 12h8M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18Z",
  "food-and-agriculture": "M12 21V8M12 8c-2-1-3-3-3-5 2 0 3 2 3 5Zm0 0c2-1 3-3 3-5-2 0-3 2-3 5Zm0 5c-2-1-4-1-5-3 2-1 4 0 5 3Zm0 0c2-1 4-1 5-3-2-1-4 0-5 3Zm0 5c-2-1-4-1-5-3 2-1 4 0 5 3Zm0 0c2-1 4-1 5-3-2-1-4 0-5 3",
  "foreign-affairs": "M12 21a9 9 0 1 0 0-18 9 9 0 0 0 0 18ZM3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18",
  "gender-equality": "M9 14a5 5 0 1 0 0-10 5 5 0 0 0 0 10Zm0 0v7M6 18h6M15 13a5 5 0 1 0 0-10M18 5l3-3m0 0h-3m3 0v3",
  health: "M9 3h6v6h6v6h-6v6H9v-6H3V9h6V3Z",
  "international-trade": "M3 17h13l-3 3M21 7H8l3-3",
  migration: "M4 12h14M14 7l5 5-5 5M4 5v14",
  "social-protection": "M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.8A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11Z",
  taxation: "M6 3h12v18l-3-2-3 2-3-2-3 2V3Zm3 6h6M9 13h6",
  "workers-rights": "M3 21h18M5 21V10h14v11M9 10V6a3 3 0 0 1 6 0v4M10 15h4",
};

export default function TopicIcon({ code }: { code: string }) {
  return (
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="square"
      aria-hidden="true"
    >
      <path d={PATHS[code] ?? PATHS["foreign-affairs"]} />
    </svg>
  );
}
