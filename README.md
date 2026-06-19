# Nama Anggota Kelompok:
- Brithany Zhafira Nurranty (203012510016)
- Nalurisa Izma Mardiana (203012510003)

# PGCB Power System Interactive Dashboard

## Deskripsi
Proyek ini merupakan dashboard HTML interaktif berbasis Bokeh untuk analisis sistem tenaga listrik PGCB.
Dashboard dikembangkan dari proyek UTS yang sebelumnya masih berupa notebook visual statis, lalu disusun ulang
menjadi dashboard yang lebih tematik dan modular.

## Dataset
Dataset memuat variabel utama:
- datetime
- generation_mw
- demand_mw
- load_shedding
- gas
- liquid_fuel
- coal
- hydro
- solar
- wind
- india_bheramara_hvdc
- india_tripura
- india_adani
- nepal
- remarks

## Struktur Dashboard
- Dataset Overview
- National Power Overview
- Energy Mix Explorer
- Import Dependency Analysis
- Peak Demand Analyzer
- Load Shedding Investigation
- Correlation Explorer
- Storytelling Panel
- Details on Demand

## Cara Menjalankan
1. Pastikan file dataset bernama `PGCB_date_power_demand.xlsx`
2. Install dependensi:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan:
   ```bash
   python main.py
   ```
4. Hasil dashboard akan tersimpan di:
   `output/bangladesh_power_grid_dashboard.html`

## Struktur File
- `main.py` : file utama untuk menghasilkan dashboard HTML
- `data_loader.py` : membaca dataset
- `preprocessing.py` : pembersihan dan transformasi data
- `dashboard_sections.py` : seluruh komponen visual Bokeh
- `insights.py` : ringkasan insight otomatis
- `requirements.txt` : daftar library yang dibutuhkan