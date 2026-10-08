import Link from "next/link";
import styles from "./Pagination.module.css";

export default function Pagination({
  page,
  hasPrev,
  hasNext,
  href,
  labels,
}: {
  page: number;
  hasPrev: boolean;
  hasNext: boolean;
  href: (page: number) => string;
  labels: { newer: string; older: string; page: string };
}) {
  if (!hasPrev && !hasNext) return null;
  return (
    <nav className={styles.pager}>
      {hasPrev ? <Link href={href(page - 1)}>← {labels.newer}</Link> : <span />}
      <span className={styles.current}>{labels.page.replace("{n}", String(page))}</span>
      {hasNext ? <Link href={href(page + 1)}>{labels.older} →</Link> : <span />}
    </nav>
  );
}
