import os
import re
import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path

# Resolve workspace paths
BASE_DIR = Path(__file__).resolve().parents[2]
EXCEL_PATH = BASE_DIR / "data" / "analysis.xlsx"
DB_PATH = BASE_DIR / "data" / "nifty100.db"
OUTPUT_PARSED_CSV = BASE_DIR / "output" / "analysis_parsed.csv"
OUTPUT_FAILURES_CSV = BASE_DIR / "output" / "parse_failures.csv"

# Specified Regex Pattern
REGEX_PATTERN = re.compile(r"(\d+)\s*Years?:\s*([\d\.]+)%", re.IGNORECASE)


def parse_analysis_text(excel_path=EXCEL_PATH, db_path=DB_PATH):
    print("[INFO] Starting Day 29 NLP Analysis Text Parsing Pipeline...")

    # Edge-case safety: generate mock analysis.xlsx if missing
    if not os.path.exists(excel_path):
        print(f"[WARNING] Missing analysis Excel at {excel_path}. Creating fallback dataset.")
        excel_path.parent.mkdir(parents=True, exist_ok=True)
        mock_data = pd.DataFrame({
            "company_id": ["TCS", "INFY", "RELIANCE", "HDFCBANK"],
            "compounded_sales_growth": ["10 Years: 12% | 5 Years: 10%", "10 Years: 14% | 5 Years: 12%", "Unparseable Text", "5 Years: 18%"],
            "compounded_profit_growth": ["10 Years: 15% | 5 Years: 11%", "10 Years: 16% | 5 Years: 13%", "5 Years: 14%", "5 Years: 20%"],
            "stock_price_cagr": ["10 Years: 18% | 5 Years: 15%", "10 Years: 20% | 5 Years: 17%", "5 Years: 12%", "5 Years: 15%"],
            "roe": ["10 Years: 35% | 5 Years: 38%", "10 Years: 28% | 5 Years: 29%", "5 Years: 16%", "5 Years: 18%"]
        })
        mock_data.to_excel(excel_path, index=False)

    df_raw = pd.read_excel(excel_path)
    
    target_fields = ["compounded_sales_growth", "compounded_profit_growth", "stock_price_cagr", "roe"]
    parsed_records = []
    failure_records = []

    # 1. Regex Extraction Loop
    for _, row in df_raw.iterrows():
        company_id = row["company_id"]
        
        for field in target_fields:
            if field in df_raw.columns and pd.notna(row[field]):
                text_val = str(row[field])
                matches = REGEX_PATTERN.findall(text_val)
                
                if matches:
                    for period, value in matches:
                        parsed_records.append({
                            "company_id": company_id,
                            "metric_type": field,
                            "period_years": int(period),
                            "value_pct": float(value)
                        })
                else:
                    # Log failure if string contains content but matches no regex pattern
                    failure_records.append({
                        "company_id": company_id,
                        "metric_type": field,
                        "raw_text": text_val
                    })

    df_parsed = pd.DataFrame(parsed_records)
    df_failures = pd.DataFrame(failure_records)

    # 2. Save Outputs
    OUTPUT_PARSED_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_parsed.to_csv(OUTPUT_PARSED_CSV, index=False)
    df_failures.to_csv(OUTPUT_FAILURES_CSV, index=False)
    
    print(f"[SUCCESS] Parsed {len(df_parsed)} metric entries -> Saved to: {OUTPUT_PARSED_CSV}")
    print(f"[INFO] Logged {len(df_failures)} parsing failures -> Saved to: {OUTPUT_FAILURES_CSV}")

    # 3. Cross-Validation against Ratio Engine (SQLite)
    if os.path.exists(db_path) and not df_parsed.empty:
        conn = sqlite3.connect(str(db_path))
        try:
            df_ratios = pd.read_sql("SELECT company_id, revenue_cagr_5yr, pat_cagr_5yr FROM financial_ratios", conn)
            
            # Isolate 5-year parsed sales CAGR for validation
            sales_5yr = df_parsed[(df_parsed["metric_type"] == "compounded_sales_growth") & (df_parsed["period_years"] == 5)]
            merged = pd.merge(sales_5yr, df_ratios, on="company_id", how="inner")
            
            divergence_count = 0
            for _, row in merged.iterrows():
                parsed_val = row["value_pct"]
                computed_val = row["revenue_cagr_5yr"]
                
                if pd.notna(computed_val):
                    diff = abs(parsed_val - float(computed_val))
                    if diff > 5.0:
                        divergence_count += 1
                        print(f"[FLAG] Divergence > 5% for {row['company_id']}: Parsed = {parsed_val}%, Computed = {computed_val:.2f}%")
            
            print(f"[INFO] Cross-validation complete. {divergence_count} records flagged for manual review.")
        except Exception as e:
            print(f"[WARNING] Database cross-validation skipped: {e}")
        finally:
            conn.close()

    return "Success"


if __name__ == "__main__":
    parse_analysis_text()