from data_loader import load_votes
from analysis_agent import analyze_policy, generate_ai_insight


_DIVIDER = "=" * 40


def _print_summary(summary: dict) -> None:
    for group, counts in sorted(summary.items()):
        n_for = counts["FOR"]
        n_against = counts["AGAINST"]
        n_abstain = counts["ABSTAIN"]
        print(f"  {group:<14}  FOR: {n_for:<3}  AGAINST: {n_against:<3}  ABSTAIN: {n_abstain}")


def _run_analysis(votes_df, topic: str) -> None:
    try:
        summary = analyze_policy(votes_df, topic)
    except ValueError as exc:
        print(f"\n[!] {exc}\n")
        return

    insight = generate_ai_insight(summary, topic)

    print(f"\n{_DIVIDER}")
    print("EU POLICY ANALYSIS")
    print(f"Topic: {topic}")
    print(_DIVIDER)
    print("\nVOTING SUMMARY:")
    _print_summary(summary)
    print("\nAI INSIGHT:")
    print(f"  {insight}")
    print(f"\n{_DIVIDER}\n")


def main() -> None:
    print("\nEU Policy Intelligence Agent initialized")
    print("Loading voting data...\n")

    votes_df = load_votes()
    available = sorted(votes_df["policy_topic"].unique().tolist())
    topic_lookup = {t.lower(): t for t in available}

    print("Available topics:")
    for topic in available:
        print(f"  • {topic}")
    print('\nType a topic name to analyse it, or "exit" to quit.\n')

    while True:
        try:
            user_input = input("Topic > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if not user_input:
            continue
        if user_input.lower() == "exit":
            print("Goodbye.")
            break

        canonical = topic_lookup.get(user_input.lower())
        if canonical is None:
            print(f"\n[!] Topic not found: '{user_input}'")
            print("    Available topics:")
            for t in available:
                print(f"      • {t}")
            print()
            continue

        _run_analysis(votes_df, canonical)


if __name__ == "__main__":
    main()
