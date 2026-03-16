from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt


IN_FP = Path("artifacts/phase1/expert1_phase1_chart_data.csv")
OUT_FP = Path("artifacts/phase1/chart_bucket_edge.png")


def main() -> None:
    if not IN_FP.exists():
        raise FileNotFoundError(f"Input file not found: {IN_FP}")

    df = pd.read_csv(IN_FP)

    required_cols = ["max_prob", "aligned_move_3m"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}. Found columns: {list(df.columns)}")

    # Keep only usable rows
    work = df[["max_prob", "aligned_move_3m"]].dropna().copy()

    # Confidence buckets
    bins = [0.5, 0.6, 0.7, 0.8, 0.9, 1.000001]
    labels = ["0.5–0.6", "0.6–0.7", "0.7–0.8", "0.8–0.9", "0.9–1.0"]

    work["prob_bucket"] = pd.cut(
        work["max_prob"],
        bins=bins,
        labels=labels,
        right=False,
        include_lowest=True
    )

    bucket_df = (
        work.groupby("prob_bucket", observed=False)["aligned_move_3m"]
        .mean()
        .reindex(labels)
        .reset_index()
    )

    plt.figure(figsize=(10, 6))
    plt.bar(bucket_df["prob_bucket"].astype(str), bucket_df["aligned_move_3m"])
    plt.axhline(0, linewidth=1)

    plt.title("Ruru — Average 3-Minute Aligned Move by Signal Confidence")
    plt.xlabel("Signal confidence bucket")
    plt.ylabel("Average aligned move after 3m (%)")

    plt.tight_layout()
    plt.savefig(OUT_FP, dpi=200, bbox_inches="tight")
    plt.close()

    print(f"[done] wrote {OUT_FP}")
    print("\nBucket summary:")
    print(bucket_df.to_string(index=False))


if __name__ == "__main__":
    main()