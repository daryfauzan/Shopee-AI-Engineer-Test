import os
import tracemalloc
from collections import Counter

import pandas as pd
from dotenv import load_dotenv
from download_data import download_data

load_dotenv("../.env")

CHUNK_SIZE = 50_000

USE_COLS = [
    "Customer Id",
    "Company",
    "City",
    "Country",
    "Email",
    "Subscription Date",
]


def process_csv(file_path: str, chunk_size: int = CHUNK_SIZE):
    tracemalloc.start()

    total_rows = 0

    # Aggregations
    country_counts = Counter()
    subscription_counts = Counter()

    # Data quality
    missing_counts = Counter()

    duplicate_emails = Counter()

    invalid_email_count = 0

    email_pattern = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"

    earliest_subscription = None
    latest_subscription = None

    for chunk_number, chunk in enumerate(
        pd.read_csv(
            file_path,
            usecols=USE_COLS,
            chunksize=chunk_size,
        ),
        start=1,
    ):
        total_rows += len(chunk)

        # --------------------------------------------------
        # Data Quality
        # --------------------------------------------------

        missing = chunk.isna().sum()

        for column, count in missing.items():
            missing_counts[column] += count

        country_counts.update(chunk["Country"].dropna())

        # duplicate_customer_ids.update(customer_ids)
        # emails = chunk["Email"].dropna()

        # duplicate_emails.update(emails)

        # # --------------------------------------------------
        # # Email validation
        # # --------------------------------------------------

        valid_email_mask = chunk["Email"].notna() & chunk["Email"].str.match(
            email_pattern, na=False
        )

        invalid_email_count += chunk["Email"].notna().sum() - valid_email_mask.sum()

        # # --------------------------------------------------
        # # Subscription dates
        # # --------------------------------------------------

        dates = pd.to_datetime(chunk["Subscription Date"], errors="coerce")

        valid_dates = dates.dropna()

        if not valid_dates.empty:
            chunk_earliest = valid_dates.min()
            chunk_latest = valid_dates.max()

            if earliest_subscription is None or chunk_earliest < earliest_subscription:
                earliest_subscription = chunk_earliest

            if latest_subscription is None or chunk_latest > latest_subscription:
                latest_subscription = chunk_latest

            # Aggregate by month
            months = valid_dates.dt.to_period("M")

            subscription_counts.update(months.astype(str))

        current, peak = tracemalloc.get_traced_memory()

        print(
            f"Chunk {chunk_number:>3} | "
            f"Rows: {total_rows:>10,} | "
            f"Current: {current / 1024 / 1024:>8.2f} MB | "
            f"Peak: {peak / 1024 / 1024:>8.2f} MB"
        )

    # ------------------------------------------------------
    # Final results
    # ------------------------------------------------------

    duplicate_email_count = sum(count > 1 for count in duplicate_emails.values())

    return {
        "total_rows": total_rows,
        "country_counts": country_counts,
        "subscription_counts": subscription_counts,
        "missing_counts": missing_counts,
        "duplicate_emails": duplicate_email_count,
        "invalid_email_count": invalid_email_count,
        "earliest_subscription": earliest_subscription,
        "latest_subscription": latest_subscription,
    }


def print_results(results):
    print("\n" + "=" * 60)
    print("CUSTOMER DATA ANALYSIS")
    print("=" * 60)

    print(f"\nTotal customers: {results['total_rows']:,}")

    # Countries
    print("\nTop 10 Countries:")

    for country, count in results["country_counts"].most_common(10):
        print(f"  {country}: {count:,}")

    # Subscriptions
    print("\nSubscription Trends:")

    for month, count in sorted(results["subscription_counts"].items()):
        print(f"  {month}: {count:,}")

    # Data quality
    print("\nData Quality:")
    print(f"  Invalid Emails: {results['invalid_email_count']:,}")

    print("\nMissing Values:")
    for column, count in results["missing_counts"].most_common():
        if count > 0:
            percentage = count / results["total_rows"] * 100
            print(f"  {column}: {count:,} ({percentage:.2f}%)")

    # Subscription range
    print("\nSubscription Date Range:")
    print(f"  Earliest: {results['earliest_subscription']}")
    print(f"  Latest: {results['latest_subscription']}")


if __name__ == "__main__":
    FILE_PATH = download_data(
        url=os.environ["LARGE_CSV_FILE_URL"],
        filename=os.environ["LARGE_CSV_FILE_NAME"],
        target_path=os.environ["DATA_DIR_PATH"],
    )

    results = process_csv(str(FILE_PATH))
    print_results(results)
