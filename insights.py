import pandas as pd


def generate_insights(df: pd.DataFrame) -> dict:

    if df.empty:
        return {
            "demand": "Tidak ada data demand.",
            "generation": "Tidak ada data generation.",
            "import": "Tidak ada data impor."
        }

    peak_demand_row = (
        df.loc[df["demand_mw"].idxmax()]
        if "demand_mw" in df.columns
        else None
    )

    peak_generation_row = (
        df.loc[df["generation_mw"].idxmax()]
        if "generation_mw" in df.columns
        else None
    )

    avg_import = (
        df["total_import"].mean()
        if "total_import" in df.columns
        else None
    )

    insights = {}

    # Demand Insight
    if peak_demand_row is not None:

        insights["demand"] = (
            f"Demand tertinggi terjadi pada "
            f"{peak_demand_row['datetime']} "
            f"dengan nilai "
            f"{peak_demand_row['demand_mw']:,.0f} MW."
        )

    else:

        insights["demand"] = (
            "Tidak tersedia informasi demand."
        )

    # Generation Insight
    if peak_generation_row is not None:

        insights["generation"] = (
            f"Generation tertinggi tercatat pada "
            f"{peak_generation_row['datetime']} "
            f"sebesar "
            f"{peak_generation_row['generation_mw']:,.0f} MW."
        )

    else:

        insights["generation"] = (
            "Tidak tersedia informasi generation."
        )

    # Import Insight
    if avg_import is not None:

        insights["import"] = (
            f"Rata-rata total impor listrik "
            f"adalah {avg_import:,.2f} MW."
        )

    else:

        insights["import"] = (
            "Tidak tersedia informasi impor."
        )

    return insights

def generate_peak_insights(df: pd.DataFrame) -> dict:

    peak_hour_table = (
        df.groupby("hour", as_index=False)["demand_mw"].mean()
        if "demand_mw" in df.columns
        else pd.DataFrame()
    )

    peak_hour = None

    if not peak_hour_table.empty:

        peak_hour = int(
            peak_hour_table.loc[
                peak_hour_table["demand_mw"].idxmax(),
                "hour"
            ]
        )

    max_load_shedding_row = (
        df.loc[df["load_shedding"].idxmax()]
        if "load_shedding" in df.columns
        else None
    )

    return {

        "peak_hour":
            f"Secara rata-rata, demand tertinggi terjadi pada pukul {peak_hour:02d}:00."
            if peak_hour is not None
            else "Tidak tersedia informasi peak hour.",

        "load_shedding":
            f"Load shedding maksimum terjadi pada {max_load_shedding_row['datetime']} dengan nilai {max_load_shedding_row['load_shedding']:,.0f} MW."
            if max_load_shedding_row is not None
            else "Tidak tersedia informasi load shedding."
    }

def generate_correlation_insights(df: pd.DataFrame) -> dict:

    avg_gap = (
        df["gap_demand_generation"].mean()
        if "gap_demand_generation" in df.columns
        else 0
    )

    return {

        "dataset_size":
            f"Analisis dilakukan terhadap {len(df):,} observasi.",

        "average_gap":
            f"Rata-rata gap demand dan generation adalah {avg_gap:,.2f} MW."
    }