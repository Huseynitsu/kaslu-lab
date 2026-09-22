"""One-off Excel analysis for professor log."""
import pandas as pd
import numpy as np
from pathlib import Path

path = Path(r"c:\Users\Huseyn\Desktop\Copy of 侯赛因.xlsx")
out = Path(__file__).resolve().parents[1] / "excel_analysis.txt"

lines = []
xl = pd.ExcelFile(path)
lines.append(f"SHEETS: {xl.sheet_names}")

for sn in xl.sheet_names:
    raw = pd.read_excel(path, sheet_name=sn, header=None)
    lines.append(f"\n=== {sn} shape {raw.shape} ===")
    for i in range(min(3, len(raw))):
        row = [str(v) if pd.notna(v) else "" for v in raw.iloc[i]]
        lines.append(f"Row{i}: " + " | ".join(row))

    df = pd.read_excel(path, sheet_name=sn, header=[0, 1])
    lines.append(f"\nMulti-index columns ({len(df.columns)}):")
    for c in df.columns:
        lines.append(f"  {c}")

    dates = pd.to_datetime(df.iloc[:, 0], errors="coerce").dropna()
    lines.append(f"\nDate rows: {len(dates)}")
    if len(dates):
        lines.append(f"From: {dates.min()} To: {dates.max()}")

    # numeric summary for key columns (flat names)
    flat = ["_".join(str(x) for x in c if str(x) != "nan").strip("_") for c in df.columns]
    df.columns = flat
    lines.append("\nFlat column names:")
    for i, n in enumerate(flat):
        lines.append(f"  [{i}] {n}")

    # sample data
    lines.append("\nFirst 3 data rows (selected cols):")
    sel = [c for c in flat if any(k in c for k in ["Date", "Duration", "NH4", "Removal", "TN", "HRT", "ANR"])]
    if sel:
        lines.append(df[sel[:12]].head(3).to_string())

    lines.append("\nLast 3 data rows:")
    if sel:
        lines.append(df[sel[:12]].tail(3).to_string())

    # check for NO2, NO3, pH, temp, FA, FNA, DO, COD
    all_text = " ".join(flat) + " " + raw.astype(str).to_string()
    for kw in ["NO2", "NO3", "pH", "PH", "Temp", "temperature", "FA", "FNA", "DO", "COD", "亚硝", "硝"]:
        lines.append(f"Keyword '{kw}': {'YES' if kw.lower() in all_text.lower() or kw in all_text else 'NO'}")

    # compute removal rate from NH4 if possible
    inf_cols = [c for c in flat if "NH4" in c and "Influent" in c and "浓度" in c or ("NH4" in c and "Influent" in c)]
    # try simpler: col names from analysis
    nh4_inf = None
    nh4_eff1 = None
    for c in flat:
        if "NH4" in c and "Influent" in c and "浓度" in c:
            nh4_inf = c
        if c.startswith("Reactor(1)_") and "浓度" in c:
            nh4_eff1 = c
    if nh4_inf and nh4_eff1 and nh4_inf in df.columns and nh4_eff1 in df.columns:
        inf = pd.to_numeric(df[nh4_inf], errors="coerce")
        eff = pd.to_numeric(df[nh4_eff1], errors="coerce")
        calc = (inf - eff) / inf * 100
        excel_rem = None
        for c in flat:
            if "Removal rate" in c and c.endswith("(1)"):
                excel_rem = c
                break
        lines.append(f"\nNH4 removal check (Reactor1): influent col={nh4_inf}, effluent col={nh4_eff1}")
        if excel_rem and excel_rem in df.columns:
            ex = pd.to_numeric(df[excel_rem], errors="coerce")
            diff = (calc - ex).abs()
            lines.append(f"Excel removal col: {excel_rem}")
            lines.append(f"Mean abs diff calc vs excel: {diff.mean():.4f}")
            lines.append(f"Max abs diff: {diff.max():.4f}")

out.write_text("\n".join(lines), encoding="utf-8")
print("Wrote", out)
