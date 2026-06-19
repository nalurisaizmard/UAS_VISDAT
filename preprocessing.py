import pandas as pd
import numpy as np


NUMERIC_COLS = [
    "generation_mw", "demand_mw", "load_shedding",
    "gas", "liquid_fuel", "coal", "hydro", "solar", "wind",
    "india_bheramara_hvdc", "india_tripura", "india_adani", "nepal"
]

ZERO_FILL_COLS = [
    "load_shedding", "gas", "liquid_fuel", "coal", "hydro",
    "solar", "wind", "india_bheramara_hvdc", "india_tripura",
    "india_adani", "nepal"
]

IMPORT_COLS = [
    "india_bheramara_hvdc", "india_tripura", "india_adani", "nepal"
]

ENERGY_COLS = [
    "gas", "liquid_fuel", "coal", "hydro", "solar", "wind"
]


def preprocess_pgcb_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Hapus baris dengan nilai tidak wajar (outlier ekstrem)
    BATAS_MAX_MW = 20000  # nilai maksimum wajar untuk sistem listrik Bangladesh

    if "generation_mw" in df.columns:
        df = df[df["generation_mw"] <= BATAS_MAX_MW]

    if "demand_mw" in df.columns:
        df = df[df["demand_mw"] <= BATAS_MAX_MW]
        
    if "datetime" not in df.columns:
        raise ValueError("Kolom 'datetime' tidak ditemukan pada dataset.")

    df["datetime"] = pd.to_datetime(df["datetime"], errors="coerce")
    df = df.dropna(subset=["datetime"]).sort_values("datetime").drop_duplicates()

    for col in NUMERIC_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ZERO_FILL_COLS:
        if col in df.columns:
            df[col] = df[col].fillna(0)

    if "remarks" in df.columns:
        df["remarks"] = df["remarks"].fillna("Normal").astype(str).str.strip()
        df["remarks"] = df["remarks"].replace({
            "EveningPeak": "Evening_Peak",
            "DayPeak": "Day_Peak",
            "": "Normal",
            "nan": "Normal",
            "None": "Normal"
        })
    else:
        df["remarks"] = "Normal"

    df["year"] = df["datetime"].dt.year
    df["month"] = df["datetime"].dt.month
    df["day"] = df["datetime"].dt.day
    df["hour"] = df["datetime"].dt.hour
    df["date"] = df["datetime"].dt.date

    available_import_cols = [c for c in IMPORT_COLS if c in df.columns]
    available_energy_cols = [c for c in ENERGY_COLS if c in df.columns]

    df["total_import"] = df[available_import_cols].sum(axis=1) if available_import_cols else 0
    df["energy_mix_total"] = df[available_energy_cols].sum(axis=1) if available_energy_cols else 0

    if "demand_mw" in df.columns and "generation_mw" in df.columns:
        df["gap_demand_generation"] = df["demand_mw"] - df["generation_mw"]
    else:
        df["gap_demand_generation"] = np.nan

    df["is_evening_peak_hour"] = df["hour"].between(17, 20)
    df["is_day_peak_hour"] = df["hour"].between(10, 12)

    return df


def make_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    summary = {
        "metric": [
            "Total Observations",
            "Date Start",
            "Date End",
            "Average Demand (MW)",
            "Average Generation (MW)",
            "Maximum Demand (MW)",
            "Maximum Generation (MW)",
            "Total Load Shedding",
            "Average Gap (MW)",
            "Average Total Import (MW)"
        ],
        "value": [
            f"{len(df):,}",
            str(df["datetime"].min()),
            str(df["datetime"].max()),
            round(df["demand_mw"].mean(), 2) if "demand_mw" in df.columns else None,
            round(df["generation_mw"].mean(), 2) if "generation_mw" in df.columns else None,
            round(df["demand_mw"].max(), 2) if "demand_mw" in df.columns else None,
            round(df["generation_mw"].max(), 2) if "generation_mw" in df.columns else None,
            round(df["load_shedding"].sum(), 2) if "load_shedding" in df.columns else None,
            round(df["gap_demand_generation"].mean(), 2) if "gap_demand_generation" in df.columns else None,
            round(df["total_import"].mean(), 2) if "total_import" in df.columns else None
        ]
    }
    return pd.DataFrame(summary)


def hourly_profile(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["demand_mw", "generation_mw", "load_shedding", "total_import"] if c in df.columns]
    out = df.groupby("hour", as_index=False)[cols].mean()
    return out.sort_values("hour")


def monthly_profile(df: pd.DataFrame) -> pd.DataFrame:
    cols = [c for c in ["demand_mw", "generation_mw", "load_shedding", "total_import"] if c in df.columns]
    out = df.groupby(["year", "month"], as_index=False)[cols].mean()
    out["month_label"] = out["year"].astype(str) + "-" + out["month"].astype(str).str.zfill(2)
    return out


def get_energy_mix_long(df: pd.DataFrame) -> pd.DataFrame:
    energy_cols = [c for c in ENERGY_COLS if c in df.columns]
    long_df = df[["datetime"] + energy_cols].copy()
    return long_df.melt(id_vars="datetime", var_name="source", value_name="mw")


def get_import_long(df: pd.DataFrame) -> pd.DataFrame:
    import_cols = [c for c in IMPORT_COLS if c in df.columns]
    long_df = df[["datetime"] + import_cols].copy()
    return long_df.melt(id_vars="datetime", var_name="source", value_name="mw")


def correlation_matrix(df: pd.DataFrame) -> pd.DataFrame:
    corr_cols = [
        c for c in [
            "generation_mw", "demand_mw", "load_shedding", "gas", "liquid_fuel",
            "coal", "hydro", "solar", "wind", "total_import", "gap_demand_generation"
        ]
        if c in df.columns
    ]
    corr_df = df[corr_cols].corr(numeric_only=True).reset_index().rename(columns={"index": "variable"})
    return corr_df