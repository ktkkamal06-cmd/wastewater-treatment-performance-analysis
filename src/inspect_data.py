
from pathlib import Path

import pandas as pd

# Project directories
PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
REPORT_DIR = PROJECT_DIR / "reports"


def inspect_dataframe(df: pd.DataFrame, name: str) -> None:
    """Print a first-pass inspection of a dataset."""
    print("\n" + "=" * 70)
    print(f"FILE / SHEET: {name}")
    print("=" * 70)

    print(f"\nNumber of rows: {df.shape[0]:,}")
    print(f"Number of columns: {df.shape[1]:,}")

    print("\nColumn names:")
    print(df.columns.tolist())

    print("\nData types:")
    print(df.dtypes.to_string())

    print("\nMissing values per column:")
    print(df.isna().sum().to_string())

    print(f"\nDuplicate rows: {df.duplicated().sum():,}")

    print("\nFirst five rows:")
    print(df.head().to_string())

    print("\nNumerical summary:")
    print(df.describe(include="all").transpose().to_string())


def main() -> None:
    if not RAW_DIR.exists():
        raise FileNotFoundError(
            f"Data folder not found: {RAW_DIR}"
        )

    files = [
        path for path in RAW_DIR.iterdir()
        if path.is_file()
        and path.suffix.lower() in {".csv", ".xlsx", ".xls"}
    ]

    if not files:
        print(f"No CSV or Excel files found in: {RAW_DIR}")
        print("Download and extract the dataset into data/raw/.")
        return

    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    for file_path in files:
        try:
            if file_path.suffix.lower() == ".csv":
                df = pd.read_csv(file_path)
                inspect_dataframe(df, file_path.name)

            else:
                # Excel files can contain multiple sheets.
                workbook = pd.ExcelFile(file_path)
                print(f"\nExcel file: {file_path.name}")
                print(f"Sheets: {workbook.sheet_names}")

                for sheet in workbook.sheet_names:
                    df = pd.read_excel(
                        file_path,
                        sheet_name=sheet
                    )
                    inspect_dataframe(
                        df,
                        f"{file_path.name} | {sheet}"
                    )

        except Exception as error:
            print(f"\nCould not inspect {file_path.name}: {error}")


if __name__ == "__main__":
    main()
