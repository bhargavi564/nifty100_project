import sys
from loader import load_all_files
from validator import validate_data
from load_to_sqlite import load_database


def main():
    print("=" * 50)
    print("Starting ETL Pipeline")
    print("=" * 50)

    try:
        # Step 1: Extract
        print("[INFO] Step 1: Extracting data from source files...")
        load_all_files()
        print("[SUCCESS] Data extraction complete.\n")

        # Step 2: Transform
        print("[INFO] Step 2: Validating and transforming data...")
        validate_data()
        print("[SUCCESS] Data validation and transformation complete.\n")

        # Step 3: Load
        print("[INFO] Step 3: Loading data into SQLite database...")
        load_database()
        print("[SUCCESS] Data load complete.\n")

    except Exception as e:
        print("\n" + "!" * 50)
        print(f"[CRITICAL ERROR] Pipeline failed during execution!")
        print(f"Error Details: {e}")
        print("!" * 50)
        sys.exit(1)

    print("=" * 50)
    print("ETL Pipeline Completed Successfully")
    print("=" * 50)


if __name__ == "__main__":
    main()