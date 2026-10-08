import styles from "./status.module.css";

export default function Loading() {
  return (
    <div className={`container ${styles.page}`} aria-busy="true">
      <div className={styles.loading}>
        <span />
        <span />
        <span />
      </div>
    </div>
  );
}
