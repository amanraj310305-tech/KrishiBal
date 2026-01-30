import os
import re
import ast
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

# ---------- File paths ----------
CROP_CSV = r"L:\Hackaton\jharkhand_crop_recommendations_with_month_numbers (1).csv"
DIST_CSV = r"L:\Hackaton\file (21).csv"

# ---------- Load data ----------
crop_df = pd.read_csv(CROP_CSV)
district_df = pd.read_csv(DIST_CSV)

# Cleanup
district_df = district_df.loc[:, ~district_df.columns.str.contains("^Unnamed")]
district_df = district_df.rename(columns={
    "Available_N": "N",
    "Available_P": "P",
    "Available_K": "K",
    "pH": "ph",
    "Rainfall": "rainfall"
})

FEATURES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]

# Prepare training data
for f in FEATURES:
    if f in crop_df.columns:
        crop_df[f] = pd.to_numeric(crop_df[f], errors="coerce")
if "label" not in crop_df.columns:
    raise KeyError("Crop CSV must contain a 'label' column")
crop_df = crop_df.fillna(crop_df.mean(numeric_only=True))

X = crop_df[[c for c in FEATURES if c in crop_df.columns]].copy()
y = crop_df["label"].astype(str).copy()

model = RandomForestClassifier(n_estimators=200, random_state=42)
model.fit(X, y)

# ---------- Month parsing ----------
MONTH_WORDS = {
    "january":1,"jan":1,"february":2,"feb":2,"march":3,"mar":3,"april":4,"apr":4,
    "may":5,"june":6,"jun":6,"july":7,"jul":7,"august":8,"aug":8,"september":9,"sep":9,"sept":9,
    "october":10,"oct":10,"november":11,"nov":11,"december":12,"dec":12
}

def parse_month_input(text):
    if not text:
        return None
    s = str(text).lower().strip()
    m = re.search(r'\b(\d{1,2})\b', s)
    if m:
        v = int(m.group(1))
        if 1 <= v <= 12:
            return v
    for name, num in MONTH_WORDS.items():
        if name in s:
            return num
    numwords = {"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12}
    for w,nv in numwords.items():
        if w in s:
            return nv
    return None

# ---------- Crop months mapping ----------
def parse_month_cell(cell):
    months = set()
    if pd.isna(cell):
        return months
    s = str(cell).strip()
    try:
        if s.startswith('[') and s.endswith(']'):
            lst = ast.literal_eval(s)
            for v in lst:
                if 1 <= int(v) <= 12:
                    months.add(int(v))
            return months
    except:
        pass
    s_low = s.lower()
    for d in re.findall(r'\d{1,2}', s_low):
        v = int(d)
        if 1 <= v <= 12:
            months.add(v)
    MONTH_NAME = {**MONTH_WORDS}
    for name, num in MONTH_NAME.items():
        if name in s_low:
            months.add(num)
    for a,b in re.findall(r'(\d{1,2})\s*-\s*(\d{1,2})', s_low):
        a=int(a); b=int(b)
        if a <= b:
            for i in range(a,b+1):
                if 1<=i<=12: months.add(i)
        else:
            for i in range(a,13): months.add(i)
            for i in range(1,b+1): months.add(i)
    return months

month_col = "ideal_month_numbers" if "ideal_month_numbers" in crop_df.columns else "ideal_months" if "ideal_months" in crop_df.columns else None
crop_months = {}
if month_col:
    for idx, row in crop_df.iterrows():
        lab = str(row["label"])
        months = parse_month_cell(row.get(month_col))
        if lab not in crop_months:
            crop_months[lab] = set()
        crop_months[lab].update(months)

# ---------- Recommend crop function ----------
def recommend_crop(district_name, month_number=None):
    dist_col = "District" if "District" in district_df.columns else "district"
    mask = district_df[dist_col].astype(str).str.strip().str.lower() == str(district_name).strip().lower()
    if not mask.any():
        return f"❌ District '{district_name}' not found."
    row = district_df.loc[mask].iloc[0]

    feat = {}
    for f in X.columns:
        if f in district_df.columns:
            val = row.get(f, None)
            try:
                feat[f] = float(val) if not pd.isna(val) else float(X[f].mean())
            except:
                feat[f] = float(X[f].mean())
        else:
            feat[f] = float(X[f].mean())
    feat_df = pd.DataFrame([feat])[X.columns]

    try:
        prob_array = model.predict_proba(feat_df)[0]
        classes = list(model.classes_)
        probs = dict(zip(classes, prob_array))
    except Exception:
        pred = model.predict(feat_df)[0]
        return f"{pred}, {pred}, {pred}"

    candidate_labels = [lab for lab, months in crop_months.items() if month_number in months] if month_number else None
    if candidate_labels:
        cand_probs = {lab: probs.get(lab,0.0) for lab in candidate_labels}
        if not any(p > 0 for p in cand_probs.values()):
            best_label = max(probs.items(), key=lambda x: x[1])[0]
        else:
            best_label = max(cand_probs.items(), key=lambda x: x[1])[0]
    else:
        best_label = max(probs.items(), key=lambda x: x[1])[0]

    return f"{best_label}, {best_label}, {best_label}"
