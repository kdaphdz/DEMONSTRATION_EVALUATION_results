import pandas as pd
import matplotlib.pyplot as plt

# --------------------------------------------------
# Configuration
# --------------------------------------------------

INPUT_FILE = "data.csv"

OUTPUT_PDF = "energy_consumption.pdf"
OUTPUT_PNG = "energy_consumption.png"

TITLE = "Energy Consumption Across CI/CD Platforms"

COLORS = {
    ("GitHub", "Package"): "#C62828",        # Red
    ("GitHub", "Cores"): "#EF9A9A",          # Light red
    ("Azure DevOps", "Package"): "#1565C0",  # Blue
    ("Azure DevOps", "Cores"): "#90CAF9",    # Light blue
}

ENERGY_COLUMNS = {
    "Package": "pkg_consumption_without_baseline_J",
    "Cores": "cores_consumption_without_baseline_J",
}

PLATFORMS = ["GitHub", "Azure DevOps"]

MARKERS = {
    "Package": "o",
    "Cores": "s",
}

LINESTYLES = {
    "Package": "-",
    "Cores": "--",
}

# --------------------------------------------------
# Academic style for LaTeX CAS-SC
# --------------------------------------------------

plt.rcParams.update({
    "font.family": "serif",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.labelsize": 11,
    "legend.fontsize": 9,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "axes.linewidth": 0.8,
    "lines.linewidth": 1.8,
    "lines.markersize": 5,
    "pdf.fonttype": 42,
    "ps.fonttype": 42,
    "savefig.dpi": 600,
})

# --------------------------------------------------
# Load and validate data
# --------------------------------------------------

df = pd.read_csv(INPUT_FILE)

df.columns = df.columns.str.strip()
df["platform"] = df["platform"].str.strip()
df["measurement"] = df["measurement"].astype(str).str.strip()

required_columns = [
    "platform",
    "measurement",
    *ENERGY_COLUMNS.values(),
]

missing = set(required_columns) - set(df.columns)

if missing:
    raise ValueError(
        f"Missing columns in {INPUT_FILE}: {sorted(missing)}"
    )

# Extract numeric measurement index
df["measurement_number"] = pd.to_numeric(
    df["measurement"].str.extract(r"(\d+)")[0],
    errors="raise",
).astype(int)

# Display measurements from 1 instead of 0
df["measurement_index"] = df["measurement_number"] + 1

# Ensure energy columns are numeric
for column in ENERGY_COLUMNS.values():
    df[column] = pd.to_numeric(df[column], errors="raise")

df = df.sort_values(["platform", "measurement_number"])

# Check platforms
for platform in PLATFORMS:
    if platform not in df["platform"].unique():
        raise ValueError(f"No measurements found for {platform}")

# --------------------------------------------------
# Create figure
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(7.0, 4.5))

# --------------------------------------------------
# Plot energy consumption
# --------------------------------------------------

for platform in PLATFORMS:

    platform_df = df[df["platform"] == platform]

    for metric, column in ENERGY_COLUMNS.items():

        ax.plot(
            platform_df["measurement_index"],
            platform_df[column],
            label=f"{platform} - {metric}",
            color=COLORS[(platform, metric)],
            marker=MARKERS[metric],
            linestyle=LINESTYLES[metric],
            linewidth=1.8,
            markersize=4.5,
            markeredgewidth=0.7,
        )

# --------------------------------------------------
# Labels and title
# --------------------------------------------------

ax.set_title(TITLE, pad=12)

ax.set_xlabel("Measurement", labelpad=7)
ax.set_ylabel("Energy Consumption (J)", labelpad=7)

measurement_indices = sorted(df["measurement_index"].unique())

ax.set_xticks(measurement_indices)

ax.set_xlim(
    min(measurement_indices) - 0.3,
    max(measurement_indices) + 0.3,
)

# --------------------------------------------------
# Grid and axes
# --------------------------------------------------

ax.grid(
    True,
    axis="y",
    linestyle=":",
    linewidth=0.7,
    alpha=0.5,
)

ax.set_axisbelow(True)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# --------------------------------------------------
# Legend OUTSIDE the plot
# --------------------------------------------------

ax.legend(
    loc="upper center",
    bbox_to_anchor=(0.5, -0.18),
    ncol=2,
    frameon=False,
    columnspacing=1.5,
    handlelength=2.5,
    handletextpad=0.6,
    borderaxespad=0,
)

# --------------------------------------------------
# Layout
# --------------------------------------------------

# Explicitly reserve space for the legend
fig.subplots_adjust(
    left=0.13,
    right=0.98,
    top=0.87,
    bottom=0.29,
)

# --------------------------------------------------
# Export publication-quality figures
# --------------------------------------------------

fig.savefig(
    OUTPUT_PDF,
    format="pdf",
    bbox_inches="tight",
    pad_inches=0.08,
)

fig.savefig(
    OUTPUT_PNG,
    format="png",
    dpi=600,
    bbox_inches="tight",
    pad_inches=0.08,
)

plt.show()

print(f"PDF saved to: {OUTPUT_PDF}")
print(f"PNG saved to: {OUTPUT_PNG}")