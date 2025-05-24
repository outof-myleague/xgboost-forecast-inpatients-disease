import panel as pn
import pandas as pd
import glob
import hvplot.pandas
import io
import matplotlib.pyplot as plt
import math

pn.extension("tabulator", "hvplot")

# Styling
ACCENT = "#004F9E"
styles = {
    "box-shadow": "rgba(50, 50, 93, 0.25) 0px 6px 12px -2px, rgba(0, 0, 0, 0.3) 0px 3px 7px -3px",
    "border-radius": "6px",
    "padding": "10px",
}

# Dropdown pilihan penyakit
csv_files = glob.glob("predictions_*_disease.csv")
disease_options = [f.replace("predictions_", "").replace("_disease.csv", "") for f in csv_files]
dropdown = pn.widgets.Select(name="Pilih Kode Penyakit", options=disease_options)

# Fungsi tampilkan rentang tanggal prediksi
@pn.depends(dropdown)
def display_date_range(kode_penyakit):
    df = pd.read_csv(f"predictions_{kode_penyakit}_disease.csv", index_col=0, parse_dates=True)
    min_date = df.index.min().strftime("%d %b %Y")
    max_date = df.index.max().strftime("%d %b %Y")
    return pn.pane.Markdown(f"**Rentang Tanggal Prediksi:** {min_date} – {max_date}")

# Fungsi grafik ringkasan top penyakit
def generate_summary_plot():
    summary_data = []
    for file in glob.glob("predictions_*_disease.csv"):
        df = pd.read_csv(file, index_col=0, parse_dates=True)
        kode_penyakit = file.replace("predictions_", "").replace("_disease.csv", "")
        total_kasus = math.ceil(df["Frequency"].sum())
        summary_data.append({"Kode Penyakit": kode_penyakit, "Total Kasus": total_kasus})
    
    df_summary = pd.DataFrame(summary_data).sort_values(by="Total Kasus", ascending=False).head(10)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.barh(df_summary["Kode Penyakit"], df_summary["Total Kasus"], color="#004F9E", edgecolor="black")
    ax.bar_label(bars, padding=5)
    ax.set_xlabel("Prediksi Jumlah Kasus")
    ax.set_ylabel("Kode Penyakit (ICD)")
    ax.set_title("Grafik Prediksi 10 Jumlah Kasus Penyakit Terbanyak Pasien Rawat Inap (Desember 2023-Desember 2024)")
    ax.invert_yaxis()
    plt.tight_layout()
    
    return fig

# Fungsi menyimpan gambar matplotlib
def simpan_gambar_png(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    return buf

# Fungsi dashboard utama
@pn.depends(dropdown)
def update_dashboard(kode_penyakit):
    df = pd.read_csv(f"predictions_{kode_penyakit}_disease.csv", index_col=0, parse_dates=True)
    df["Frequency"] = pd.to_numeric(df["Frequency"], errors="coerce").fillna(0)
    
    df_month = df.resample("M").sum()
    count = len(df)
    total = df["Frequency"].sum()
    total_rounded = math.ceil(total)
    avg_daily = df["Frequency"].mean()
    max_val = df["Frequency"].max()
    max_day = df["Frequency"].idxmax().strftime("%Y-%m-%d")
    
    # Indikator
    indicators = pn.FlexBox(
        pn.indicators.Number(name="Jumlah Hari", value=count, format="{value:,.0f}", styles=styles),
        pn.indicators.Number(name="Total Prediksi", value=total_rounded, format="{value:,.0f}", styles=styles),
        pn.indicators.Number(name="Rata-rata Kasus", value=round(avg_daily), format="{value:,.2f}", styles=styles),
        pn.indicators.Number(name="Hari Tertinggi", value=int(max_val), format="{value:,.0f}", styles=styles),
    )
    
    # Insight
    insight = pn.pane.Markdown(f"""
    ### Insight
    - Puncak kasus terjadi pada **{max_day}** dengan **{int(max_val)} kasus**.
    - Rata-rata harian: **{avg_daily:.2f} kasus**
    - Total prediksi selama periode: **{total_rounded} kasus**
    """, styles=styles)
    
    # Plot bulanan dan harian
    line_plot_daily = df.hvplot.line(
        y="Frequency", xlabel="Tanggal", ylabel="Jumlah Kasus Penyakit/hari",
        title=f"Prediksi Harian - {kode_penyakit}", color="#94C83D",
        line_width=2, height=500, width=1000, grid=True, hover_cols="all"
    ) * df.hvplot.scatter(y="Frequency", size=6, color="red")

    line_plot_month = df_month.hvplot.line(
        y="Frequency", xlabel="Bulan", ylabel="Total Kasus Penyakit/bulan",
        title=f"Prediksi Bulanan - {kode_penyakit}", color="#94C83D",
        line_width=2, height=500, width=1000, rot=45, grid=True, hover_cols="all"
    )
    
    # Tabel harian dan bulanan
    df_harian = df.copy().reset_index()
    df_harian["Tanggal"] = df_harian["index"].dt.strftime("%Y-%m-%d")
    tab_harian = pn.widgets.Tabulator(df_harian[["Tanggal", "Frequency"]], pagination="remote", page_size=10)
    
    df_bulanan = df_month.copy().reset_index()
    df_bulanan["Bulan"] = df_bulanan["index"].dt.strftime("%Y-%m")
    tab_bulanan = pn.widgets.Tabulator(df_bulanan[["Bulan", "Frequency"]], pagination="remote", page_size=12)

    tabs = pn.Tabs(
        ("Data Harian", tab_harian),
        ("Agregasi Bulanan", tab_bulanan),
        height=400,
        margin=20,
    )
    
    plot_tabs = pn.Tabs(
        ("Plot Harian", line_plot_daily),
        ("Plot Bulanan", line_plot_month),
        ("Agregasi Bulanan", tab_bulanan),
        ("Agregasi Harian", tab_harian),
        height=400,
        margin=20,
    )
    
    return pn.Column(
        pn.pane.Markdown("## Indikator Prediksi"),
        indicators,
        insight,
        plot_tabs,
        # tabs,
        sizing_mode="stretch_width"
    )

# Ringkasan
fig_summary = generate_summary_plot()
plot_pane = pn.pane.Matplotlib(fig_summary, tight=True, width=700, height=350)

btn_download = pn.widgets.FileDownload(
    label="Download Grafik",
    callback=lambda: simpan_gambar_png(fig_summary),
    filename="grafik_prediksi.png",
    button_type="primary"
)

summary_tab = pn.Column(
    pn.pane.Markdown("## Visualisasi Grafik Prediksi Penyakit Terbanyak Pasien Rawat Inap"),
    plot_pane,
    btn_download,
    sizing_mode="stretch_width"
)

tabs = pn.Tabs(
    ("Data Harian & Bulanan", update_dashboard),
    ("Grafik Prediksi", summary_tab),
)

# Logo
logo = pn.pane.Image("rspb_logo.png", width=200, height=100)

# Template
pn.template.FastListTemplate(
    title="Dashboard Prediksi Penyakit Rawat Inap RS Pertamina Balikpapan",
    sidebar=[
        logo,
        "## Filter Data",
        pn.pane.Markdown("Pilih kode penyakit untuk melihat grafik dan data prediksi."),
        dropdown,
        pn.panel(display_date_range),
],
    main=[
        pn.Column(tabs, sizing_mode="stretch_width", styles={"overflow-y": "auto", "max-height": "80vh"})
    ],
    accent=ACCENT,
).servable()