import os
import webbrowser

from bokeh.io import output_file, save
from bokeh.layouts import column, row
from bokeh.models import Div

from data_loader import load_pgcb_data
from preprocessing import preprocess_pgcb_data
from insights import (
    generate_insights,
    generate_peak_insights,
    generate_correlation_insights
)

from dashboard_sections import (
    make_page_style,
    make_hero,
    make_section_heading,
    make_peak_story_panel,
    make_correlation_story_panel,
    make_kpi_row,
    make_energy_story_panel,
    make_power_overview_chart,
    make_gap_chart,
    make_energy_mix_chart,
    make_import_chart,
    make_hourly_peak_chart,
    make_load_shedding_scatter,
    make_correlation_heatmap,
    make_story_panel,
    make_detail_table,
    make_dashboard_tabs,
    _chart_card,
)
DATA_FILE = "PGCB_date_power_demand.xlsx"

OUTPUT_DIR = "output"

OUTPUT_HTML = os.path.join(
    OUTPUT_DIR,
    "index.html"
)

#Energy Mix
def get_energy_long(df):

    cols = [
        c for c in
        ["gas", "liquid_fuel", "coal", "hydro", "solar", "wind"]
        if c in df.columns
    ]

    return df[
        ["datetime"] + cols
    ].melt(
        id_vars="datetime",
        var_name="source",
        value_name="mw"
    )

#Import
def get_import_long(df):

    cols = [
        c for c in
        [
            "india_bheramara_hvdc",
            "india_tripura",
            "india_adani",
            "nepal"
        ]
        if c in df.columns
    ]

    return df[
        ["datetime"] + cols
    ].melt(
        id_vars="datetime",
        var_name="source",
        value_name="mw"
    )

#Hourly Profile
def get_hourly_profile(df):

    cols = [
        c for c in
        [
            "demand_mw",
            "generation_mw",
            "load_shedding",
            "total_import"
        ]
        if c in df.columns
    ]

    return (
        df.groupby("hour", as_index=False)[cols]
        .mean()
        .sort_values("hour")
    )

#Correlation
def get_corr_df(df):

    corr_cols = [
        c for c in
        [
            "generation_mw",
            "demand_mw",
            "load_shedding",
            "gas",
            "liquid_fuel",
            "coal",
            "hydro",
            "solar",
            "wind",
            "total_import",
            "gap_demand_generation"
        ]
        if c in df.columns
    ]

    return (
        df[corr_cols]
        .corr(numeric_only=True)
        .reset_index()
        .rename(columns={"index": "variable"})
    )

#Main Function
def main():

    if not os.path.exists(DATA_FILE):
        raise FileNotFoundError(
            f"File '{DATA_FILE}' tidak ditemukan."
        )

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    raw_df = load_pgcb_data(DATA_FILE)

    df = preprocess_pgcb_data(raw_df)

    energy_long = get_energy_long(df)

    import_long = get_import_long(df)

    hourly_df = get_hourly_profile(df)

    corr_df = get_corr_df(df)

    insight_dict = generate_insights(df)
    peak_insight_dict = generate_peak_insights(df)

    corr_insight_dict = generate_correlation_insights(df)

    overview_tab = column(


       row(
            column(
                _chart_card(make_power_overview_chart(df)),
                sizing_mode="stretch_width"
            ),
            column(
                _chart_card(make_gap_chart(df)),
                sizing_mode="stretch_width"
            ),
            sizing_mode="stretch_width",
            spacing=25
        ),
        Div(text="<div style='height:25px'></div>"),
        make_story_panel(insight_dict),

        sizing_mode="stretch_width"
    )

    
    energy_tab = column(

        row(
            column(
                _chart_card(
                    make_energy_mix_chart(energy_long)
                ),
                sizing_mode="stretch_width"
            ),

            column(
                _chart_card(
                    make_import_chart(import_long)
                ),
                sizing_mode="stretch_width"
            ),

            sizing_mode="stretch_width",
            spacing=25
        ),

        Div(text="<div style='height:25px'></div>"),

        make_energy_story_panel(df),

        sizing_mode="stretch_width"
    )

    peak_tab = column(

        row(
            column(
                _chart_card(
                    make_hourly_peak_chart(hourly_df)
                ),
                sizing_mode="stretch_width"
            ),

            column(
                _chart_card(
                    make_load_shedding_scatter(df)
                ),
                sizing_mode="stretch_width"
            ),

            sizing_mode="stretch_width",
            spacing=25
        ),

        Div(text="<div style='height:25px'></div>"),

        make_peak_story_panel(
            peak_insight_dict
        ),

        sizing_mode="stretch_width"
    )
    
    detail_tab = column(

        _chart_card(
            make_correlation_heatmap(corr_df)
        ),

        Div(text="<div style='height:25px'></div>"),

        make_correlation_story_panel(
            corr_insight_dict
        ),

        Div(text="<div style='height:25px'></div>"),

        _chart_card(
            make_detail_table(
                df,
                limit=200
            )
        ),

        sizing_mode="stretch_width"
    )
    
    tabs = make_dashboard_tabs(
        overview_tab,
        energy_tab,
        peak_tab,
        detail_tab
    )

    layout = column(

        make_page_style(),

        Div(text="<div style='height:12px'></div>"),

        make_hero(),

        Div(text="<div style='height:30px'></div>"),

        make_kpi_row(df),

        Div(text="<div style='height:30px'></div>"),

        column(
            tabs,
            sizing_mode="stretch_width",
            styles={
                "background": "#FFFFFF",
                "border": "1px solid #E7ECF2",
                "border-radius": "24px",
                "padding": "15px 20px 20px 20px",
                "box-shadow": "0 8px 30px rgba(15,42,67,.06)"
            }
        ),

        Div(text="<div style='height:20px'></div>"),

        

        sizing_mode="stretch_width",
        margin=(0, 40, 0, 40)
        )
    output_file(
        OUTPUT_HTML,
        title="PGCB Power System Dashboard"
    )

    save(layout)

    with open(OUTPUT_HTML, "r", encoding="utf-8") as f:
        html = f.read()

    inject = """
    <style>

    html, body{
        margin:0;
        padding:0;
        background:#F7F9FC;
    }

    body{
        display:flex;
        justify-content:center;
    }

   div[data-root-id]{
    max-width:1400px !important;
    width:95% !important;
    margin:auto !important;
    padding-left:20px !important;
    padding-right:20px !important;
    box-sizing:border-box !important;
    }

    </style>
    """

    html = html.replace("</head>", inject + "</head>")

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"Dashboard berhasil dibuat: {OUTPUT_HTML}")

    webbrowser.open(
        f"file:///{os.path.abspath(OUTPUT_HTML)}"
    )

if __name__ == "__main__":
    main()