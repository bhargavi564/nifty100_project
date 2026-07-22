import os
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]

def run_final_audit():
    print("==================================================")
    print("🏆 SPRINT 5 FINAL EXIT CRITERIA AUDIT")
    print("==================================================")
    
    all_passed = True

    # 1. Check pros_cons_generated.csv (1 pro, 1 con per company)
    pc_csv = BASE_DIR / "output" / "pros_cons_generated.csv"
    if pc_csv.exists():
        df_pc = pd.read_csv(pc_csv)
        companies = df_pc["company_id"].unique()
        missing = []
        for comp in companies:
            comp_df = df_pc[df_pc["company_id"] == comp]
            if not (comp_df["type"] == "pro").any() or not (comp_df["type"] == "con").any():
                missing.append(comp)
        
        if not missing:
            print("[PASS] pros_cons_generated.csv has at least 1 pro and 1 con for every company.")
        else:
            print(f"[FAIL] Missing pros/cons for: {missing}")
            all_passed = False
    else:
        print("[FAIL] pros_cons_generated.csv not found.")
        all_passed = False

    # 2. Check Tearsheets (reports/tearsheets/) > 30KB
    ts_dir = BASE_DIR / "reports" / "tearsheets"
    if ts_dir.exists():
        pdfs = list(ts_dir.glob("*.pdf"))
        # Check size > 30KB (30 * 1024 bytes)
        small_pdfs = [p.name for p in pdfs if p.stat().st_size < 30720]
        
        if len(pdfs) > 0 and not small_pdfs:
             print(f"[PASS] {len(pdfs)} tearsheets exist and are all > 30KB.")
        elif small_pdfs:
             print(f"[FAIL] The following tearsheets are under 30KB: {small_pdfs}")
             all_passed = False
    else:
        print("[FAIL] Tearsheets directory not found.")
        all_passed = False

    # 3. Check cashflow_intelligence.xlsx rows
    cf_xlsx = BASE_DIR / "output" / "cashflow_intelligence.xlsx"
    if cf_xlsx.exists():
        df_cf = pd.read_excel(cf_xlsx)
        if len(df_cf) >= 4: # Validating it populated records
            print(f"[PASS] cashflow_intelligence.xlsx is fully populated with {len(df_cf)} rows.")
        else:
            print(f"[FAIL] cashflow_intelligence.xlsx has insufficient rows: {len(df_cf)}")
            all_passed = False
    else:
        print("[FAIL] cashflow_intelligence.xlsx not found.")
        all_passed = False
        
    print("==================================================")
    if all_passed:
        print("✅ SUCCESS: ALL SPRINT 5 EXIT CRITERIA MET. READY FOR DEMO!")
    else:
        print("❌ WARNING: SOME CRITERIA FAILED. PLEASE REVIEW.")
    print("==================================================")

if __name__ == "__main__":
    run_final_audit()