import pandas as pd


def load_pgcb_data(file_path: str) -> pd.DataFrame:
    df = pd.read_excel(file_path)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]

    rename_map = {
        "generationmw": "generation_mw",
        "demandmw": "demand_mw",
        "loadshedding": "load_shedding",
        "liquidfuel": "liquid_fuel",
        "indiabheramarahvdc": "india_bheramara_hvdc",
        "indiatripura": "india_tripura",
        "indiaadani": "india_adani"
    }

    df = df.rename(columns=rename_map)
    return df