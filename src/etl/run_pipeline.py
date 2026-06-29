from loader import load_all_files
from validator import validate_data
from load_to_sqlite import load_database


def main():

    print("Starting ETL Pipeline...\n")

    load_all_files()

    validate_data()

    load_database()

    print("\nPipeline Completed Successfully")


if __name__ == "__main__":
    main()