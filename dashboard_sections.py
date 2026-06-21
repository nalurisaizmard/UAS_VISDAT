import numpy as np
import pandas as pd
from bokeh.layouts import column, row
from bokeh.models import (
    ColumnDataSource, HoverTool, DataTable, TableColumn, Div,
    Span, LinearColorMapper, ColorBar, BasicTicker,
    TabPanel, Tabs, Band, NumeralTickFormatter, Label, BoxAnnotation,
)
from bokeh.palettes import Category10
from bokeh.plotting import figure
from bokeh.transform import factor_cmap

TITLE_COLOR  = "#0F2A43"
TEXT_COLOR   = "#3D5266"
MUTED_COLOR  = "#7587A0"
CARD_BG      = "#FFFFFF"
CARD_BORDER  = "#E4E9F2"
ACCENT       = "#2A6FA8"
ACCENT_SOFT  = "#EAF2FA"
GOLD_ACCENT  = "#C9A55C"


# ── helpers ──────────────────────────────────────────────────────────────────

def _remove_outliers(df, col, q_low=0.01, q_high=0.99):
    if col not in df.columns:
        return df
    lo, hi = df[col].quantile(q_low), df[col].quantile(q_high)
    return df[(df[col] >= lo) & (df[col] <= hi)]


def _fig(title, height=520, **kw):
    p = figure(title=title, height=height, sizing_mode="stretch_width",
               toolbar_location="right",
               tools="pan,wheel_zoom,box_zoom,reset,save", **kw)
    p.background_fill_color = "#FDFEFF"
    p.border_fill_color     = CARD_BG
    p.outline_line_color    = None
    p.title.text_font_size  = "15pt"
    p.title.text_font       = "Segoe UI, Arial, sans-serif"
    p.title.align           = "center"
    p.title.text_color      = TITLE_COLOR
    p.title.text_font_style = "bold"
    p.grid.grid_line_color  = "#F1F4F9"
    p.grid.grid_line_width  = 1
    p.xaxis.major_label_text_color  = MUTED_COLOR
    p.yaxis.major_label_text_color  = MUTED_COLOR
    p.xaxis.major_label_text_font_size = "9.5pt"
    p.yaxis.major_label_text_font_size = "9.5pt"
    p.xaxis.axis_label_text_color   = TEXT_COLOR
    p.yaxis.axis_label_text_color   = TEXT_COLOR
    p.xaxis.axis_label_text_font_style = "bold"
    p.xaxis.axis_label_text_font_size  = "11pt"
    p.yaxis.axis_label_text_font_style = "bold"
    p.yaxis.axis_label_text_font_size  = "11pt"
    p.xaxis.axis_label_standoff = 12
    p.yaxis.axis_label_standoff = 12
    p.axis.axis_line_color = "#D9E2EC"
    p.axis.major_tick_line_color = "#D9E2EC"
    p.axis.minor_tick_line_color = None
    p.min_border_left = 30
    p.min_border_bottom = 40
    p.min_border_right = 30
    p.min_border_top = 20
    return p


def _chart_card(fig_or_layout):

    return column(
        fig_or_layout,
        sizing_mode="stretch_width",
        styles={
            "background": "#FFFFFF",
            "border": "1px solid #EDF2F7",
            "border-radius": "20px",
            "padding": "15px",
            "box-shadow": "0 4px 16px rgba(15,42,67,.05)"
        }
    )


def _legend(p):
    leg = p.legend[0]

    leg.click_policy = "hide"
    leg.orientation = "vertical"
    leg.location = "top_left"

    leg.label_text_font_size = "10pt"
    leg.label_text_color = TEXT_COLOR
    leg.background_fill_color = "#FAFCFF"
    leg.background_fill_alpha = 1.0
    leg.border_line_color = "#E4E9F2"
    leg.border_line_width = 1
    leg.padding = 12
    leg.spacing = 8
    leg.glyph_width = 18
    leg.glyph_height = 12
    leg.label_standoff = 8
    leg.margin = 10

    p.legend.remove(leg)
    p.add_layout(leg, "below")


def _info_box(color_bg, color_border, color_title, title, bullets):
    items = "".join(f"<li style='margin-bottom:7px'>{b}</li>" for b in bullets)
    return Div(sizing_mode="stretch_width", text=f"""
    <div style="background:{color_bg};border:1px solid {color_border};border-radius:16px;
                padding:20px 24px;margin-top:16px;font-family:'Segoe UI',Arial,sans-serif;
                box-shadow:0 4px 14px rgba(15,42,67,0.04);">
        <div style="font-weight:700;color:{color_title};font-size:14.5px;margin-bottom:12px;
                    display:flex;align-items:center;gap:8px;">
            <span style="display:inline-block;width:6px;height:6px;border-radius:50%;
                         background:{color_title};"></span>
             {title}
        </div>
        <ul style="margin:0;padding-left:20px;color:{TEXT_COLOR};font-size:13px;line-height:1.95;">
            {items}
        </ul>
    </div>""")


def format_number(value, suffix=""):
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "-"
    return f"{value:,.2f}{suffix}"


# ── page chrome ──────────────────────────────────────────────────────────────

def make_page_style():
    return Div(text="", width=0, height=0)   # CSS sudah inline, tidak perlu tag


from bokeh.models import Div

def make_hero():
    return Div(
        sizing_mode="stretch_width",
        margin=(0, 0, 0, 0),
        styles={
            "display": "flex",
            "justify-content": "center"
        },
        text="""
    <div style="
        width:100%;
        max-width:1400px;
        background:linear-gradient(120deg,#0B2438 0%,#16395C 45%,#1F5C8F 100%);
        color:white;
        border-radius:18px;
        padding:42px 60px;
        margin:0 auto 20px auto;
        box-shadow:0 18px 40px rgba(15,42,67,0.22);
        position:relative;
        overflow:hidden;
        border:1px solid rgba(255,255,255,0.08);
    ">

        <!-- decorative circles -->
        <div style="
            position:absolute;
            top:-60px;
            right:-60px;
            width:220px;
            height:220px;
            border-radius:50%;
            background:radial-gradient(circle,rgba(255,255,255,0.08),transparent 70%);
        "></div>

        <div style="
            position:absolute;
            bottom:-80px;
            left:30%;
            width:260px;
            height:260px;
            border-radius:50%;
            background:radial-gradient(circle,rgba(201,165,92,0.10),transparent 70%);
        "></div>

        <!-- content -->
        <div style="position:relative;z-index:1;text-align:center;">

            <!-- badge -->
            <div style="
                display:inline-flex;
                align-items:center;
                gap:8px;
                padding:6px 14px;
                font-size:11px;
                font-weight:700;
                letter-spacing:.9px;
                text-transform:uppercase;
                border-radius:999px;
                background:rgba(255,255,255,.12);
                color:#EAF4FF;
                margin-bottom:16px;
                border:1px solid rgba(255,255,255,.15);
            ">
                <span style="
                    width:6px;
                    height:6px;
                    border-radius:50%;
                    background:#C9A55C;
                    display:inline-block;
                "></span>
                Interactive Dashboard — Bangladesh Power Grid (PGCB)
            </div>

            <!-- title -->
            <div style="
                font-size:32px;
                font-weight:800;
                line-height:1.2;
                margin-bottom:12px;
                letter-spacing:-0.4px;
            ">
                PGCB Power System Interactive Dashboard
            </div>

            <!-- description -->
            <div style="
                font-size:13.5px;
                line-height:1.85;
                color:rgba(255,255,255,.85);
                max-width:1000px;
                margin:0 auto 22px auto;
            ">
                Dashboard ini dirancang untuk mengeksplorasi kondisi sistem tenaga listrik PGCB
                (Power Grid Company of Bangladesh). Gunakan tab di bawah untuk menjelajahi
                demand vs generation, bauran energi, impor listrik, pola jam puncak, dan load shedding.
                Setiap grafik dilengkapi <b style="color:#F2DCA6;">tooltip interaktif</b>,
                <b style="color:#F2DCA6;">zoom</b>, dan <b style="color:#F2DCA6;">pan</b>.
            </div>

            <!-- tabs preview chips -->
            <div style="
                display:flex;
                justify-content:center;
                gap:10px;
                flex-wrap:wrap;
            ">
                <span style="
                    padding:8px 14px;
                    border-radius:11px;
                    background:rgba(255,255,255,.10);
                    color:#F5FAFF;
                    font-size:12px;
                    border:1px solid rgba(255,255,255,.12);
                ">📊 National Power Overview</span>

                <span style="
                    padding:8px 14px;
                    border-radius:11px;
                    background:rgba(255,255,255,.10);
                    color:#F5FAFF;
                    font-size:12px;
                    border:1px solid rgba(255,255,255,.12);
                ">⚡ Energy Mix Explorer</span>

                <span style="
                    padding:8px 14px;
                    border-radius:11px;
                    background:rgba(255,255,255,.10);
                    color:#F5FAFF;
                    font-size:12px;
                    border:1px solid rgba(255,255,255,.12);
                ">🌏 Import Dependency</span>

                <span style="
                    padding:8px 14px;
                    border-radius:11px;
                    background:rgba(255,255,255,.10);
                    color:#F5FAFF;
                    font-size:12px;
                    border:1px solid rgba(255,255,255,.12);
                ">🕐 Peak Demand</span>

                <span style="
                    padding:8px 14px;
                    border-radius:11px;
                    background:rgba(255,255,255,.10);
                    color:#F5FAFF;
                    font-size:12px;
                    border:1px solid rgba(255,255,255,.12);
                ">🔴 Load Shedding</span>
            </div>

        </div>
    </div>
    """
    )

def make_section_heading(title, subtitle=""):
    return Div(sizing_mode="stretch_width", text=f"""
    <table width="100%" cellpadding="0" cellspacing="0"
           style="margin-bottom:8px;font-family:'Segoe UI',Arial,sans-serif;">
        <tr><td align="center" style="padding-top:28px;padding-bottom:18px;text-align:center;">
            <div style="width:46px;height:3px;background:linear-gradient(90deg,#C9A55C,#2A6FA8);
                        border-radius:3px;margin:0 auto 14px auto;"></div>
            <div style="font-size:29px;font-weight:800;color:#0F2A43;
                        margin-bottom:10px;letter-spacing:-0.4px;text-align:center;">{title}</div>
            <center><div style="font-size:14px;color:{MUTED_COLOR};line-height:1.75;
                        max-width:720px;text-align:center;">{subtitle}</div></center>
        </td></tr>
    </table>""")


def _kpi_card(label, value, note, icon="📌", accent=None):

    accent = accent or ACCENT

    return Div(
        sizing_mode="stretch_width",
        height=135,
        text=f"""
        <div style="
            background:white;
            border:1px solid #E8EDF5;
            border-radius:22px;
            padding:18px 20px;
            height:100%;
            box-shadow:0 8px 24px rgba(15,42,67,.07);
            transition:.2s;
        ">

            <div style="
                display:flex;
                align-items:center;
                gap:15px;
            ">

                <div style="
                    width:56px;
                    height:56px;
                    border-radius:18px;
                    background:{accent}15;
                    display:flex;
                    justify-content:center;
                    align-items:center;
                    font-size:28px;
                    flex-shrink:0;
                ">
                    {icon}
                </div>

                <div>

                    <div style="
                        color:#3D5266;
                        font-size:13px;
                        font-weight:600;
                        margin-bottom:8px;
                    ">
                        {label}
                    </div>

                    <div style="
                        font-size:30px;
                        font-weight:800;
                        color:#0F2A43;
                        line-height:1;
                    ">
                        {value}
                    </div>

                    <div style="
                        color:#7587A0;
                        font-size:12px;
                        margin-top:8px;
                    ">
                        {note}
                    </div>

                </div>

            </div>

        </div>
        """
    )


def make_kpi_row(df):

    peak_demand = (
        df["demand_mw"].max()
        if "demand_mw" in df.columns
        else 0
    )

    peak_generation = (
        df["generation_mw"].max()
        if "generation_mw" in df.columns
        else 0
    )

    import_dependency = (
        (df["total_import"].mean() /
         df["demand_mw"].mean()) * 100
        if (
            "total_import" in df.columns
            and "demand_mw" in df.columns
        )
        else 0
    )

    avg_gap = (
        df["gap_demand_generation"].mean()
        if "gap_demand_generation" in df.columns
        else 0
    )


    return row(

        _kpi_card(
            "Total Observasi",
            f"{len(df):,}",
            "Jumlah seluruh data",
            "🗂️",
            "#9333EA"
        ),

        _kpi_card(
            "Demand (MW)",
            f"{peak_demand:,.0f}",
            "Peak Demand",
            "📈",
            "#2563EB"
        ),

        _kpi_card(
            "Generation (MW)",
            f"{peak_generation:,.0f}",
            "Peak Generation",
            "⚡",
            "#16A34A"
        ),

        _kpi_card(
            "Gap (MW)",
            format_number(avg_gap),
            "Average Gap",
            "⚠️",
            "#F59E0B"
        ),


        _kpi_card(
            "Import (%)",
            f"{import_dependency:.1f}%",
            "Import Dependency",
            "🌏",
            "#06B6D4"
        ),

        sizing_mode="stretch_width",
        spacing=25,
        margin=(0, 0, 0, 0)
    )

def make_executive_summary(df):
    peak_demand = (
        df["demand_mw"].max()
        if "demand_mw" in df.columns
        else 0
    )

    peak_generation = (
        df["generation_mw"].max()
        if "generation_mw" in df.columns
        else 0
    )

    peak_hour = (
        df.groupby("hour")["demand_mw"]
        .mean()
        .idxmax()
        if "hour" in df.columns
        else "-"
    )

    import_dependency = (
        (df["total_import"].mean() /
         df["demand_mw"].mean()) * 100
        if (
            "total_import" in df.columns
            and "demand_mw" in df.columns
        )
        else 0
    )

    return Div(
        sizing_mode="stretch_width",
        text=f"""
        <div style="
            background:white;
            border:1px solid #E4E9F2;
            border-radius:18px;
            padding:22px 26px;
            box-shadow:0 8px 22px rgba(15,42,67,0.05);
            margin-bottom:16px;
        ">

            <div style="
                font-size:18px;
                font-weight:800;
                color:#0F2A43;
                margin-bottom:14px;">
                📌 Executive Summary
            </div>

            <ul style="
                margin:0;
                padding-left:20px;
                line-height:2;
                color:#3D5266;
                font-size:13px;">

                <li>
                    Peak Demand mencapai
                    <b>{peak_demand:,.0f} MW</b>
                </li>

                <li>
                    Peak Generation mencapai
                    <b>{peak_generation:,.0f} MW</b>
                </li>

                <li>
                    Jam puncak rata-rata terjadi pada
                    <b>{peak_hour}:00</b>
                </li>

                <li>
                    Ketergantungan impor listrik sekitar
                    <b>{import_dependency:.2f}%</b>
                </li>

                <li>
                    Load shedding cenderung meningkat
                    saat demand tinggi
                </li>

            </ul>
        </div>
        """
    )

def make_power_overview_chart(df):
    dfc = _remove_outliers(df.copy(), "demand_mw")
    dfc = _remove_outliers(dfc, "generation_mw").sort_values("datetime")
    src = ColumnDataSource(dfc)

    p = _fig("Demand vs Generation Listrik Nasional", x_axis_type="datetime")
    p.line("datetime", "generation_mw", source=src, line_width=2, color="#1F4E79", alpha=0.6, legend_label="Generation (Pembangkitan)")
    p.line("datetime", "demand_mw",     source=src, line_width=2.5, color="#E63946", legend_label="Demand (Kebutuhan)")
    p.add_layout(Band(base="datetime", lower="generation_mw", upper="demand_mw",
                      source=src, fill_alpha=0.12, fill_color="#D1495B", line_color=None))

    p.xaxis.axis_label = "Tanggal / Waktu"
    p.yaxis.axis_label = "Daya (MW)"
    p.yaxis.formatter  = NumeralTickFormatter(format="0,0")
    p.add_tools(HoverTool(
        tooltips=[("Waktu","@datetime{%d %b %Y %H:%M}"),
                  ("Demand","@demand_mw{0,0} MW"),
                  ("Generation","@generation_mw{0,0} MW")],
        formatters={"@datetime":"datetime"}, mode="vline"))
    _legend(p)
    return p


def make_gap_chart(df):
    dfc = _remove_outliers(df.copy(), "gap_demand_generation").sort_values("datetime")
    dfc["gap_pos"] = dfc["gap_demand_generation"].clip(lower=0)
    dfc["gap_neg"] = dfc["gap_demand_generation"].clip(upper=0)
    src = ColumnDataSource(dfc)

    p = _fig("Gap: Demand − Generation", x_axis_type="datetime")
    p.line("datetime","gap_demand_generation", source=src,
           line_width=1.5, color="#1A1A2E", alpha=0.8, legend_label="Gap (MW)")
    p.add_layout(Band(base="datetime", lower=0,         upper="gap_pos",
                      source=src, fill_alpha=0.75, fill_color="#E63946", line_color=None))
    p.add_layout(Band(base="datetime", lower="gap_neg", upper=0,
                      source=src, fill_alpha=0.70, fill_color="#2DC653", line_color=None))
    p.add_layout(Span(location=0, dimension="width",
                      line_dash="dashed", line_color=MUTED_COLOR, line_width=1.2))

    p.xaxis.axis_label = "Tanggal / Waktu"
    p.yaxis.axis_label = "Gap Daya (MW)"
    p.yaxis.formatter  = NumeralTickFormatter(format="0,0")
    p.add_tools(HoverTool(
        tooltips=[("Waktu","@datetime{%d %b %Y %H:%M}"),
                  ("Gap","@gap_demand_generation{0,0} MW"),
                  ("Ket.","+ = Defisit 🔴  /  − = Surplus 🟢")],
        formatters={"@datetime":"datetime"}, mode="vline"))
    _legend(p)
    return p


def make_energy_mix_chart(long_df):
    cleaned = []
    for s in long_df["source"].unique():
        t = long_df[long_df["source"]==s].copy()
        cleaned.append(_remove_outliers(t,"mw"))
    long_df = pd.concat(cleaned).sort_values("datetime")

    labels = {"gas":"Gas Alam","liquid_fuel":"Bahan Bakar Cair","coal":"Batu Bara",
              "hydro":"Hidroelektrik","solar":"Surya (Solar)","wind":"Angin (Wind)"}
    colors = {"gas":"#2196F3","liquid_fuel":"#FF5722","coal":"#6D4C41",
              "hydro":"#00ACC1","solar":"#FFB300","wind":"#43A047"}

    p = _fig("Komposisi Bauran Energi Domestik", x_axis_type="datetime")
    for s in sorted(long_df["source"].dropna().unique()):
        cds = ColumnDataSource(long_df[long_df["source"]==s].copy())
        p.line("datetime","mw", source=cds, line_width=2.2,
               color=colors.get(s,"#999"), legend_label=labels.get(s,s), alpha=0.9)

    p.xaxis.axis_label = "Tanggal / Waktu"
    p.yaxis.axis_label = "Daya Dihasilkan (MW)"
    p.yaxis.formatter  = NumeralTickFormatter(format="0,0")
    p.add_tools(HoverTool(
        tooltips=[("Waktu","@datetime{%d %b %Y %H:%M}"),
                  ("Sumber","@source"),("Daya","@mw{0,0} MW")],
        formatters={"@datetime":"datetime"}))
    _legend(p)
    return p


def make_import_chart(long_df):
    cleaned = []
    for s in long_df["source"].unique():
        t = long_df[long_df["source"]==s].copy()
        cleaned.append(_remove_outliers(t,"mw"))
    long_df = pd.concat(cleaned).sort_values("datetime")

    labels = {"india_bheramara_hvdc":"India — Bheramara HVDC",
              "india_tripura":"India — Tripura",
              "india_adani":"India — Adani","nepal":"Nepal"}
    colors = {"india_bheramara_hvdc":"#1565C0","india_tripura":"#F9A825",
              "india_adani":"#00897B","nepal":"#E53935"}

    p = _fig("Impor Listrik dari Luar Negeri", x_axis_type="datetime")
    for s in sorted(long_df["source"].dropna().unique()):
        cds = ColumnDataSource(long_df[long_df["source"]==s].copy())
        p.line("datetime","mw", source=cds, line_width=2.2,
               color=colors.get(s,"#999"), legend_label=labels.get(s,s), alpha=0.9)

    p.xaxis.axis_label = "Tanggal / Waktu"
    p.yaxis.axis_label = "Daya Diimpor (MW)"
    p.yaxis.formatter  = NumeralTickFormatter(format="0,0")
    p.add_tools(HoverTool(
        tooltips=[("Waktu","@datetime{%d %b %Y %H:%M}"),
                  ("Sumber","@source"),("Daya","@mw{0,0} MW")],
        formatters={"@datetime":"datetime"}))
    _legend(p)
    return p


def make_hourly_peak_chart(hourly_df):
    src = ColumnDataSource(hourly_df)
    p   = _fig("Rata-rata Demand per Jam dalam Sehari", height=500)

    p.line("hour","demand_mw",   source=src, line_width=3, color="#C1121F", legend_label="Avg Demand (MW)")
    p.scatter("hour","demand_mw",source=src, size=8,   color="#C1121F", legend_label="Avg Demand (MW)")
    peak_hour = hourly_df.loc[
        hourly_df["demand_mw"].idxmax(),
            "hour"
        ]

    peak_value = hourly_df["demand_mw"].max()

    p.add_layout(
            Label(
                x=peak_hour,
                y=peak_value,
                text=f"Peak: {peak_hour}:00",
                text_font_size="10pt",
                text_color="#C1121F"
            )
        )

    p.add_layout(BoxAnnotation(left=17,right=20, fill_alpha=0.14, fill_color="#F4A261"))
    p.add_layout(BoxAnnotation(left=10,right=12, fill_alpha=0.12, fill_color="#2A9D8F"))

    # label annotasi jam puncak — Y diposisikan dinamis
    y_min = hourly_df["demand_mw"].min() if "demand_mw" in hourly_df.columns else 0
    p.add_layout(Label(x=17.2, y=y_min, text="Puncak Sore",
                       text_font_size="9pt", text_color="#C2410C"))
    p.add_layout(Label(x=10.2, y=y_min, text="Puncak Pagi",
                       text_font_size="9pt", text_color="#166534"))

    p.xaxis.axis_label = "Jam (0–23)"
    p.yaxis.axis_label = "Avg Demand (MW)"
    p.yaxis.formatter  = NumeralTickFormatter(format="0,0")
    p.x_range.start = 0
    p.x_range.end   = 23
    p.add_tools(HoverTool(tooltips=[
        ("Jam","@hour:00"),("Avg Demand","@demand_mw{0,0} MW"),
        ("Avg Generation","@generation_mw{0,0} MW"),("Avg Impor","@total_import{0,0} MW")]))
    _legend(p)
    return p


def make_load_shedding_scatter(df):

    dfc = _remove_outliers(df.copy(), "demand_mw")
    dfc = _remove_outliers(dfc, "load_shedding", q_low=0.0, q_high=0.99)
    dfc = dfc[dfc["load_shedding"] > 0].copy()

    dfc["remarks"] = dfc["remarks"].fillna("normal").astype(str)

    factors = sorted(dfc["remarks"].unique().tolist())
    pal = Category10[max(3, len(factors))][:len(factors)]

    label_map = {
        "normal": "Normal",
        "day_peak": "Day Peak",
        "evening_peak": "Evening Peak"
    }

    p = _fig("Load Shedding vs Demand", height=500)

    # Membuat renderer terpisah untuk setiap kategori
    for remark, color in zip(factors, pal):

        temp = dfc[dfc["remarks"] == remark]

        source = ColumnDataSource(temp)

        p.scatter(
            x="demand_mw",
            y="load_shedding",
            source=source,
            size=7,
            alpha=0.65,
            color=color,
            legend_label=label_map.get(remark, remark)
        )

    p.xaxis.axis_label = "Demand (MW)"
    p.yaxis.axis_label = "Load Shedding (MW)"

    p.xaxis.formatter = NumeralTickFormatter(format="0,0")
    p.yaxis.formatter = NumeralTickFormatter(format="0,0")

    hover = HoverTool(
        tooltips=[
            ("Waktu", "@datetime{%d %b %Y %H:%M}"),
            ("Demand", "@demand_mw{0,0} MW"),
            ("Load Shedding", "@load_shedding{0,0} MW"),
            ("Kategori", "@remarks")
        ],
        formatters={
            "@datetime": "datetime"
        }
    )

    p.add_tools(hover)

    _legend(p)

    return p

def make_correlation_heatmap(corr_df):
    melted = corr_df.melt(id_vars="variable", var_name="variable_2", value_name="correlation")
    melted["lbl"] = melted["correlation"].round(2).astype(str)

    lmap = {"generation_mw":"Generation","demand_mw":"Demand","load_shedding":"Load Shedding",
            "gas":"Gas","liquid_fuel":"BBM","coal":"Batu Bara","hydro":"Hidro",
            "solar":"Surya","wind":"Angin","total_import":"Total Impor","gap_demand_generation":"Gap D-G"}
    melted["variable"]   = melted["variable"].map(lambda x: lmap.get(x,x))
    melted["variable_2"] = melted["variable_2"].map(lambda x: lmap.get(x,x))

    src      = ColumnDataSource(melted)
    y_fac    = [lmap.get(v,v) for v in corr_df["variable"].tolist()]
    x_fac    = [lmap.get(c,c) for c in corr_df.columns if c != "variable"]
    mapper   = LinearColorMapper(
        palette=["#3B82F6","#93C5FD","#DBEAFE","#FEF9C3","#FCA5A5","#DC2626"],
        low=-1, high=1)

    p = figure(title="Heatmap Korelasi Antarvariabel",
               x_range=x_fac, y_range=list(reversed(y_fac)),
               height=460, sizing_mode="stretch_width",
               toolbar_location="right", tools="pan,wheel_zoom,reset,save")
    p.background_fill_color = CARD_BG
    p.border_fill_color     = CARD_BG
    p.outline_line_color    = CARD_BORDER
    p.title.text_font_size  = "14pt"
    p.title.align           = "center"
    p.title.text_color      = TITLE_COLOR

    p.rect(x="variable_2", y="variable", width=1, height=1,
           source=src, line_color="white",
           fill_color={"field":"correlation","transform":mapper})
    p.text(x="variable_2", y="variable", text="lbl", source=src,
           text_align="center", text_baseline="middle", text_font_size="9pt")

    p.add_tools(HoverTool(tooltips=[
        ("Var 1","@variable"),("Var 2","@variable_2"),
        ("Korelasi","@correlation{0.00}")]))
    p.add_layout(ColorBar(color_mapper=mapper, ticker=BasicTicker(),
                          label_standoff=8, title="r"), "right")
    p.xaxis.major_label_orientation = 0.8
    return p


def make_story_panel(insight_dict):

    demand_text = insight_dict.get(
        "demand",
        "Tidak ada insight demand."
    )

    generation_text = insight_dict.get(
        "generation",
        "Tidak ada insight generation."
    )

    import_text = insight_dict.get(
        "import",
        "Tidak ada insight import."
    )

    return row(

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
                height:100%;
            ">
                <div style="
                    font-size:28px;
                    margin-bottom:12px;
                ">📈</div>

                <div style="
                    font-weight:700;
                    color:#0F2A43;
                    font-size:16px;
                    margin-bottom:10px;
                ">
                    Demand Insight
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    {demand_text}
                </div>
            </div>
            """,
            sizing_mode="stretch_width"
        ),

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
                height:100%;
            ">
                <div style="
                    font-size:28px;
                    margin-bottom:12px;
                ">⚡</div>

                <div style="
                    font-weight:700;
                    color:#0F2A43;
                    font-size:16px;
                    margin-bottom:10px;
                ">
                    Generation Insight
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    {generation_text}
                </div>
            </div>
            """,
            sizing_mode="stretch_width"
        ),

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
                height:100%;
            ">
                <div style="
                    font-size:28px;
                    margin-bottom:12px;
                ">🌏</div>

                <div style="
                    font-weight:700;
                    color:#0F2A43;
                    font-size:16px;
                    margin-bottom:10px;
                ">
                    Import Insight
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    {import_text}
                </div>
            </div>
            """,
            sizing_mode="stretch_width"
        ),

        sizing_mode="stretch_width",
        spacing=25
    )

def make_energy_story_panel(df):

    avg_import = (
        df["total_import"].mean()
        if "total_import" in df.columns
        else 0
    )

    energy_cols = [
        c for c in
        ["gas", "liquid_fuel", "coal", "hydro", "solar", "wind"]
        if c in df.columns
    ]

    dominant_source = "-"

    if energy_cols:
        dominant_source = (
            df[energy_cols]
            .mean()
            .idxmax()
            .replace("_", " ")
            .title()
        )

    renewable_cols = [
        c for c in ["hydro", "solar", "wind"]
        if c in df.columns
    ]

    renewable_share = 0

    if renewable_cols and energy_cols:

        renewable_share = (
            df[renewable_cols].sum().sum()
            /
            df[energy_cols].sum().sum()
        ) * 100

    return row(

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
            ">
                <div style="font-size:28px;margin-bottom:12px;">⚡</div>

                <div style="
                    font-size:16px;
                    font-weight:700;
                    color:#0F2A43;
                    margin-bottom:10px;
                ">
                    Dominant Energy Source
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    {dominant_source} merupakan sumber pembangkitan listrik utama.
                </div>
            </div>
            """,
            sizing_mode="stretch_width"
        ),

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
            ">
                <div style="font-size:28px;margin-bottom:12px;">🌏</div>

                <div style="
                    font-size:16px;
                    font-weight:700;
                    color:#0F2A43;
                    margin-bottom:10px;
                ">
                    Import Dependency
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    Rata-rata impor listrik sebesar
                    {avg_import:,.2f} MW.
                </div>
            </div>
            """,
            sizing_mode="stretch_width"
        ),

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
            ">
                <div style="font-size:28px;margin-bottom:12px;">🌱</div>

                <div style="
                    font-size:16px;
                    font-weight:700;
                    color:#0F2A43;
                    margin-bottom:10px;
                ">
                    Renewable Contribution
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    Kontribusi energi terbarukan mencapai
                    {renewable_share:.2f}% dari total pembangkitan.
                </div>
            </div>
            """,
            sizing_mode="stretch_width"
        ),

        sizing_mode="stretch_width",
        spacing=25
    )

def make_detail_table(df, limit=200):
    show = [c for c in ["datetime","demand_mw","generation_mw","load_shedding",
                         "gas","liquid_fuel","coal","hydro","solar","wind",
                         "india_bheramara_hvdc","india_tripura","india_adani","nepal",
                         "total_import","gap_demand_generation","remarks"] if c in df.columns]
    labels = {"datetime":"Waktu","demand_mw":"Demand (MW)","generation_mw":"Generation (MW)",
              "load_shedding":"Load Shedding (MW)","gas":"Gas (MW)","liquid_fuel":"BBM (MW)",
              "coal":"Batu Bara (MW)","hydro":"Hidro (MW)","solar":"Surya (MW)","wind":"Angin (MW)",
              "india_bheramara_hvdc":"Bheramara HVDC","india_tripura":"Tripura","india_adani":"Adani",
              "nepal":"Nepal","total_import":"Total Impor (MW)","gap_demand_generation":"Gap D-G (MW)",
              "remarks":"Kategori"}
    dff = df.sort_values("datetime", ascending=False)[show].head(limit).copy()
    return DataTable(
            source=ColumnDataSource(dff),

            columns=[
                TableColumn(
                    field=c,
                    title=labels.get(c, c)
                )
                for c in dff.columns
            ],

            height=420,

            sizing_mode="stretch_width",

            index_position=None,

            reorderable=False,

            sortable=True,

            selectable=True
        )


def make_dashboard_tabs(overview_layout, energy_layout, peak_layout, detail_layout):

    tabs = Tabs(
        tabs=[
            TabPanel(child=overview_layout, title="📊 Overview"),
            TabPanel(child=energy_layout, title="⚡ Energy & Import"),
            TabPanel(child=peak_layout, title="🕐 Peak & Load Shedding"),
            TabPanel(child=detail_layout, title="🔍 Korelasi & Detail Data"),
        ]
    )

    tabs.margin = (0,0,0,0)
    tabs.sizing_mode = "stretch_width"

    return tabs


def make_peak_story_panel(insight_dict):

    return row(

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
            ">
                <div style="font-size:28px;margin-bottom:12px;">🕐</div>

                <div style="
                    font-weight:700;
                    font-size:16px;
                    color:#0F2A43;
                    margin-bottom:10px;
                ">
                    Peak Hour
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    {insight_dict["peak_hour"]}
                </div>
            </div>
            """,

            sizing_mode="stretch_width"
        ),

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
            ">
                <div style="font-size:28px;margin-bottom:12px;">🔴</div>

                <div style="
                    font-weight:700;
                    font-size:16px;
                    color:#0F2A43;
                    margin-bottom:10px;
                ">
                    Load Shedding
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    {insight_dict["load_shedding"]}
                </div>
            </div>
            """,

            sizing_mode="stretch_width"
        ),

        sizing_mode="stretch_width",
        spacing=25
    )

def make_correlation_story_panel(insight_dict):

    return row(

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
            ">
                <div style="font-size:28px;margin-bottom:12px;">📊</div>

                <div style="
                    font-size:16px;
                    font-weight:700;
                    color:#0F2A43;
                    margin-bottom:10px;
                ">
                    Dataset Size
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    {insight_dict["dataset_size"]}
                </div>
            </div>
            """,

            sizing_mode="stretch_width"
        ),

        Div(
            text=f"""
            <div style="
                background:white;
                border:1px solid #E7ECF2;
                border-radius:20px;
                padding:20px;
                box-shadow:0 4px 18px rgba(15,42,67,.05);
            ">
                <div style="font-size:28px;margin-bottom:12px;">⚖️</div>

                <div style="
                    font-size:16px;
                    font-weight:700;
                    color:#0F2A43;
                    margin-bottom:10px;
                ">
                    Average Gap
                </div>

                <div style="
                    color:#5C6B7A;
                    line-height:1.8;
                    font-size:13px;
                ">
                    {insight_dict["average_gap"]}
                </div>
            </div>
            """,

            sizing_mode="stretch_width"
        ),

        sizing_mode="stretch_width",
        spacing=25
    )