import styles from "./votes.module.css";

export default function ResultTag({
  result,
  labels,
}: {
  result: "ADOPTED" | "REJECTED" | null;
  labels: { adopted: string; rejected: string };
}) {
  if (!result) return null;
  const adopted = result === "ADOPTED";
  return (
    <span className={`${styles.result} ${adopted ? styles.adopted : styles.rejected}`}>
      {adopted ? labels.adopted : labels.rejected}
    </span>
  );
}
