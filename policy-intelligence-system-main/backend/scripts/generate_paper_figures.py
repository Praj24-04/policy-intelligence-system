"""
generate_paper_figures.py
=========================
Generates publication-quality figures for the PolicyIQ IEEE research paper.

Figures produced
----------------
  Fig 1 — UMAP 2D Cluster Map  (sector-colored, HDBSCAN label annotated)
  Fig 2 — UMAP 2D Cluster Map  (cluster-colored, convex-hull boundaries)
  Fig 3 — Cluster Size Bar Chart
  Fig 4 — Cluster Confidence Distribution (violin)
  Fig 5 — Sector × Cluster Heat-map
  Fig 6 — Recommendation Score Distribution (box + strip per sector)
  Fig 7 — Country Recommendation Frequency Bar Chart
  Fig 8 — Cross-Sector Overlap Matrix (Jaccard heat-map)

All output images are saved to:
  <backend root>/paper_figures/

Usage (run from backend/ folder):
  ../.venv/Scripts/python scripts/generate_paper_figures.py
"""

import sys
import json
import logging
import warnings
from pathlib import Path

warnings.filterwarnings("ignore")

# ─── Path Setup ───────────────────────────────────────────────────────────────
_backend_root = Path(__file__).parent.parent
if str(_backend_root) not in sys.path:
    sys.path.insert(0, str(_backend_root))

OUTPUT_DIR = _backend_root / "paper_figures"
OUTPUT_DIR.mkdir(exist_ok=True)

# ─── Matplotlib / Seaborn Setup ───────────────────────────────────────────────
import numpy as np
import matplotlib
matplotlib.use("Agg")  # non-interactive backend — safe for scripts
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.patheffects as pe
import seaborn as sns

# IEEE paper style: crisp, minimal, legible at 2-column width
plt.rcParams.update({
    "font.family":        "DejaVu Serif",
    "font.size":          10,
    "axes.titlesize":     11,
    "axes.labelsize":     10,
    "xtick.labelsize":    8.5,
    "ytick.labelsize":    8.5,
    "legend.fontsize":    8.5,
    "figure.dpi":         300,
    "savefig.dpi":        300,
    "savefig.bbox":       "tight",
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.linewidth":     0.8,
    "grid.linewidth":     0.5,
    "grid.alpha":         0.4,
    "lines.linewidth":    1.2,
})

# ─── Logger ───────────────────────────────────────────────────────────────────
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

# ─── DB & ML Imports ──────────────────────────────────────────────────────────
log.info("Loading app modules...")
from app.database import get_connection
from app.ml.embedding_store import get_all_embeddings

# ─── Sector / Cluster colour palettes ─────────────────────────────────────────
SECTOR_COLORS = {
    "AI Governance":         "#4361EE",   # vivid blue
    "Cybersecurity":         "#F72585",   # hot pink
    "Data Privacy":          "#3ECFB0",   # teal
    "ESG Policies":          "#F9A825",   # amber
    "Healthcare AI":         "#B5179E",   # purple
    "Financial Regulation":  "#E85D04",   # orange
    "IoT and Robotics":      "#7209B7",   # violet
    "POSH Policies":         "#4CC9F0",   # light blue
    "Other":                 "#888888",   # grey fallback
}

CLUSTER_PALETTE = [
    "#4361EE", "#F72585", "#3ECFB0", "#F9A825",
    "#B5179E", "#E85D04", "#7209B7", "#4CC9F0",
]
NOISE_COLOR = "#CCCCCC"

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 1 — Fetch data from PostgreSQL
# ═══════════════════════════════════════════════════════════════════════════════

log.info("Fetching policies from PostgreSQL...")
conn = get_connection()
try:
    rows = conn.execute(
        """
        SELECT id, title, sector, country, region,
               cluster_id, cluster_confidence, embedding
        FROM policies
        WHERE embedding IS NOT NULL
        ORDER BY id
        """
    ).fetchall()
finally:
    conn.close()

log.info(f"Fetched {len(rows)} policies with embeddings.")

if not rows:
    log.error("No policies with embeddings found. Run embed_all_policies.py first.")
    sys.exit(1)

# ─── Parse into lists ─────────────────────────────────────────────────────────
from app.ml.embedding_store import _parse_db_vector   # reuse internal helper

ids            = []
titles         = []
sectors        = []
countries      = []
regions        = []
cluster_ids    = []
confidences    = []
embeddings_raw = []

for row in rows:
    ids.append(row["id"])
    titles.append(row["title"] or "")
    sectors.append(row["sector"] or "Other")
    countries.append(row["country"] or "Unknown")
    regions.append(row["region"] or "Unknown")
    cluster_ids.append(row["cluster_id"] if row["cluster_id"] is not None else -1)
    confidences.append(float(row["cluster_confidence"] or 0.0))
    emb = _parse_db_vector(row["embedding"])
    if emb is not None:
        embeddings_raw.append(emb)

embeddings = np.array(embeddings_raw, dtype=np.float32)
cluster_ids_arr = np.array(cluster_ids, dtype=int)
confidences_arr = np.array(confidences, dtype=float)

log.info(f"Unique sectors   : {sorted(set(sectors))}")
log.info(f"Unique cluster IDs: {sorted(set(cluster_ids))}")

# ═══════════════════════════════════════════════════════════════════════════════
# STEP 2 — Run UMAP to 2D (for visualisation only)
# ═══════════════════════════════════════════════════════════════════════════════

log.info("Running UMAP 2D reduction (for visualisation)...")
import umap

reducer_2d = umap.UMAP(
    n_components=2,
    n_neighbors=15,
    min_dist=0.05,          # tighter clusters look cleaner in paper figures
    metric="cosine",
    random_state=42,
    low_memory=False,
)
coords_2d = reducer_2d.fit_transform(embeddings)
x_2d, y_2d = coords_2d[:, 0], coords_2d[:, 1]
log.info("UMAP 2D reduction complete.")


# ═══════════════════════════════════════════════════════════════════════════════
# Helper: convex hull outline for a cluster
# ═══════════════════════════════════════════════════════════════════════════════

def draw_convex_hull(ax, pts, color, alpha=0.12, linewidth=1.2):
    """Draw a filled convex hull polygon around a set of 2D points."""
    if len(pts) < 3:
        return
    try:
        from scipy.spatial import ConvexHull
        hull = ConvexHull(pts)
        verts = pts[hull.vertices]
        verts = np.vstack([verts, verts[0]])      # close the polygon
        ax.fill(verts[:, 0], verts[:, 1], color=color, alpha=alpha, zorder=0)
        ax.plot(verts[:, 0], verts[:, 1], color=color,
                linewidth=linewidth, alpha=0.55, zorder=1, linestyle="--")
    except Exception:
        pass   # too few points or co-linear → skip hull


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 1 — UMAP coloured by SECTOR
# ═══════════════════════════════════════════════════════════════════════════════

log.info("Generating Figure 1: UMAP coloured by Sector...")

unique_sectors = sorted(set(sectors))
fig, ax = plt.subplots(figsize=(6.5, 4.8))

for sector in unique_sectors:
    mask = [s == sector for s in sectors]
    color = SECTOR_COLORS.get(sector, SECTOR_COLORS["Other"])
    ax.scatter(
        x_2d[mask], y_2d[mask],
        c=color, s=14, alpha=0.75, linewidths=0,
        label=sector, zorder=2,
    )

ax.set_title("Fig. 1  —  UMAP Projection Coloured by Regulatory Sector", pad=8)
ax.set_xlabel("UMAP Dimension 1")
ax.set_ylabel("UMAP Dimension 2")
ax.legend(loc="best", framealpha=0.85, edgecolor="#cccccc",
          markerscale=1.8, handletextpad=0.4)
ax.grid(True, linestyle=":")
fig.tight_layout()
out1 = OUTPUT_DIR / "fig1_umap_by_sector.png"
fig.savefig(out1)
plt.close(fig)
log.info(f"  Saved → {out1}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 2 — UMAP coloured by HDBSCAN CLUSTER with convex hulls
# ═══════════════════════════════════════════════════════════════════════════════

log.info("Generating Figure 2: UMAP coloured by HDBSCAN Cluster...")

unique_clusters = sorted(set(cluster_ids))
fig, ax = plt.subplots(figsize=(6.5, 4.8))

has_labeled_cluster = False
for cid in unique_clusters:
    mask_bool = cluster_ids_arr == cid
    pts = coords_2d[mask_bool]

    if cid == -1:
        ax.scatter(pts[:, 0], pts[:, 1],
                   c=NOISE_COLOR, s=8, alpha=0.4, linewidths=0,
                   label="Noise / Outlier", zorder=1, marker="x")
    else:
        color = CLUSTER_PALETTE[cid % len(CLUSTER_PALETTE)]
        label = None
        if not has_labeled_cluster:
            label = f"Clustered Policies ({len(set(unique_clusters) - {-1})} Clusters)"
            has_labeled_cluster = True
        ax.scatter(pts[:, 0], pts[:, 1],
                   c=color, s=14, alpha=0.80, linewidths=0,
                   label=label, zorder=2)
        draw_convex_hull(ax, pts, color=color)

ax.set_title("Fig. 2  —  UMAP Projection Coloured by HDBSCAN Cluster", pad=8)
ax.set_xlabel("UMAP Dimension 1")
ax.set_ylabel("UMAP Dimension 2")
ax.legend(loc="upper left", framealpha=0.85, edgecolor="#cccccc",
          markerscale=1.4, handletextpad=0.4)
ax.grid(True, linestyle=":")
fig.tight_layout()
out2 = OUTPUT_DIR / "fig2_umap_by_cluster.png"
fig.savefig(out2)
plt.close(fig)
log.info(f"  Saved → {out2}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 3 — Cluster Size Bar Chart  (HORIZONTAL, sorted by size)
# ═══════════════════════════════════════════════════════════════════════════════

log.info("Generating Figure 3: Cluster size bar chart (horizontal, sorted)...")

from collections import Counter
cluster_counts = Counter(cluster_ids)

# Separate noise from real clusters
real_clusters = {k: v for k, v in cluster_counts.items() if k != -1}
noise_count   = cluster_counts.get(-1, 0)

# Sort by SIZE descending so the chart reads top-to-bottom largest→smallest
sorted_clusters = sorted(real_clusters.items(), key=lambda x: x[1], reverse=True)
cluster_labels_sorted = [f"C{k}" for k, _ in sorted_clusters]
cluster_sizes_sorted  = [v for _, v in sorted_clusters]
cluster_colors_sorted = [CLUSTER_PALETTE[k % len(CLUSTER_PALETTE)] for k, _ in sorted_clusters]

# Invert so largest appears at top of horizontal chart (y-coordinate increases bottom-to-top)
fig, ax = plt.subplots(figsize=(6.5, 9.0))
y_pos = list(range(len(cluster_labels_sorted)))

bars = ax.barh(
    y_pos,
    cluster_sizes_sorted[::-1],
    color=cluster_colors_sorted[::-1],
    edgecolor="white", linewidth=0.5, height=0.72, zorder=2
)

# Y-tick labels
ax.set_yticks(y_pos)
ax.set_yticklabels(cluster_labels_sorted[::-1], fontsize=7.5)

# Annotate bar ends with exact count
for bar, sz in zip(bars, cluster_sizes_sorted[::-1]):
    ax.text(
        bar.get_width() + 0.4, bar.get_y() + bar.get_height() / 2,
        str(sz), va="center", ha="left", fontsize=7.5, fontweight="bold"
    )

# Add summary stats box
stats_txt = (
    f"Total clusters: {len(real_clusters)}\n"
    f"Noise / outlier: {noise_count} policies\n"
    f"Largest: {cluster_sizes_sorted[0]}  |  Smallest: {cluster_sizes_sorted[-1]}"
)
ax.text(
    0.98, 0.02, stats_txt, transform=ax.transAxes,
    ha="right", va="bottom", fontsize=7.5, color="#555555",
    bbox=dict(boxstyle="round,pad=0.4", fc="#f8f8f8", ec="#cccccc", lw=0.7)
)

ax.set_title("Fig. 3  —  HDBSCAN Cluster Size Distribution\n(43 clusters, sorted by policy count)", pad=8)
ax.set_xlabel("Number of Policies")
ax.set_ylabel("Cluster ID")
ax.set_xlim(0, max(cluster_sizes_sorted) * 1.22)
ax.grid(axis="x", linestyle=":", zorder=0)
fig.tight_layout()
out3 = OUTPUT_DIR / "fig3_cluster_sizes.png"
fig.savefig(out3)
plt.close(fig)
log.info(f"  Saved → {out3}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 4 — Cluster Confidence Overview  (2-panel redesign)
#   Panel A: KDE histogram of ALL confidence scores (system-wide picture)
#   Panel B: Scatter — cluster median confidence vs cluster size
#            (identifies which large clusters have low confidence)
# ═══════════════════════════════════════════════════════════════════════════════

log.info("Generating Figure 4: Cluster confidence overview (2-panel)...")

# Pre-compute per-cluster statistics
cluster_medians = []
cluster_means   = []
cluster_stds    = []
cluster_sizes_conf = []
cluster_cids_conf  = []

for cid in sorted(real_clusters.keys()):
    mask_bool = cluster_ids_arr == cid
    conf_vals = confidences_arr[mask_bool]
    if len(conf_vals) > 0:
        cluster_medians.append(float(np.median(conf_vals)))
        cluster_means.append(float(np.mean(conf_vals)))
        cluster_stds.append(float(np.std(conf_vals)))
        cluster_sizes_conf.append(int(mask_bool.sum()))
        cluster_cids_conf.append(cid)

# All non-noise confidence values for KDE panel
all_conf = confidences_arr[cluster_ids_arr != -1]

fig, (ax_kde, ax_scatter) = plt.subplots(
    1, 2, figsize=(9.0, 4.0),
    gridspec_kw={"width_ratios": [1.2, 1]}
)

# ── Panel A: KDE histogram ──────────────────────────────────────────────────
sns.histplot(
    all_conf, bins=28, kde=False, ax=ax_kde,
    color="#4361EE", alpha=0.55, linewidth=0
)
sns.kdeplot(
    all_conf, ax=ax_kde,
    color="#1a1a6e", linewidth=1.8, bw_adjust=0.8
)
ax_kde.axvline(np.median(all_conf), color="#F72585", linewidth=1.5,
               linestyle="--", label=f"Median = {np.median(all_conf):.2f}")
ax_kde.axvline(0.5, color="#E85D04", linewidth=1.2,
               linestyle=":", label="Threshold = 0.50")
ax_kde.set_xlabel("Cluster Confidence Score")
ax_kde.set_ylabel("Policy Count")
ax_kde.set_title("(a)  Confidence Score Distribution\nacross all clustered policies", fontsize=9.5)
ax_kde.legend(fontsize=8)
ax_kde.grid(axis="y", linestyle=":", alpha=0.5)

# ── Panel B: Median confidence vs cluster size scatter ──────────────────────
sc_colors = [CLUSTER_PALETTE[c % len(CLUSTER_PALETTE)] for c in cluster_cids_conf]
ax_scatter.scatter(
    cluster_sizes_conf, cluster_medians,
    c=sc_colors, s=55, alpha=0.85, linewidths=0.4, edgecolors="white", zorder=2
)
ax_scatter.axhline(0.5, color="#E85D04", linewidth=1.2,
                   linestyle=":", label="Threshold = 0.50")

# Label only notable clusters (size > 30 or median < 0.7)
for cid, sz, med in zip(cluster_cids_conf, cluster_sizes_conf, cluster_medians):
    if sz > 30 or med < 0.70:
        ax_scatter.annotate(
            f"C{cid}",
            xy=(sz, med), xytext=(4, 3), textcoords="offset points",
            fontsize=6.5, color="#333333"
        )

ax_scatter.set_xlabel("Cluster Size (n policies)")
ax_scatter.set_ylabel("Median Confidence Score")
ax_scatter.set_title("(b)  Cluster Size vs Median Confidence\n(labelled: large or low-confidence clusters)", fontsize=9.5)
ax_scatter.set_ylim(0.2, 1.05)
ax_scatter.legend(fontsize=8)
ax_scatter.grid(linestyle=":", alpha=0.5)

fig.suptitle("Fig. 4  —  HDBSCAN Cluster Confidence Score Analysis",
             fontsize=11, fontweight="bold", y=1.01)
fig.tight_layout()
out4 = OUTPUT_DIR / "fig4_cluster_confidence.png"
fig.savefig(out4)
plt.close(fig)
log.info(f"  Saved → {out4}")


# ═══════════════════════════════════════════════════════════════════════════════
# FIGURE 5 — Sector × Cluster Heatmap  (TOP 15 clusters only)
#
# 43 clusters in one heatmap makes cells unreadably small.
# We keep only the 15 largest clusters (by policy count), which together
# contain the overwhelming majority of non-noise policies.
# ═══════════════════════════════════════════════════════════════════════════════

log.info("Generating Figure 5: Sector × Cluster heatmap (top-15 clusters)...")

# ── Select top 15 clusters by policy count ────────────────────────────────────
TOP_N_CLUSTERS = 15
top15_clusters = sorted(
    real_clusters.keys(),
    key=lambda k: real_clusters[k],
    reverse=True
)[:TOP_N_CLUSTERS]
top15_clusters_sorted = sorted(top15_clusters)  # re-sort by ID for display order

# Build the (sector × top-15) count matrix
sector_cluster_matrix = np.zeros((len(unique_sectors), TOP_N_CLUSTERS), dtype=int)

for sec, cid in zip(sectors, cluster_ids):
    if cid == -1 or cid not in top15_clusters_sorted:
        continue
    row_i = unique_sectors.index(sec)
    col_j = top15_clusters_sorted.index(cid)
    sector_cluster_matrix[row_i, col_j] += 1

# ── Build shorter display labels: "C4 (n=54)" ─────────────────────────────────
col_labels = [f"C{c}\n(n={real_clusters[c]})" for c in top15_clusters_sorted]

# ── Short sector labels to keep Y-axis clean ─────────────────────────────────
sector_short = {
    "AI Governance":      "AI Gov.",
    "Cybersecurity":      "Cyber",
    "Data Privacy":       "Data Priv.",
    "ESG Policies":       "ESG",
    "Financial Regulation": "Finance",
    "Healthcare AI":      "Health AI",
    "IoT and Robotics":   "IoT",
    "POSH Policies":      "POSH",
}
row_labels = [sector_short.get(s, s) for s in unique_sectors]

# ── Figure ─────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10.0, 4.4))

cmap_blue = LinearSegmentedColormap.from_list(
    "iceblue", ["#F0F4FF", "#4361EE"], N=256
)
im = ax.imshow(
    sector_cluster_matrix, cmap=cmap_blue, aspect="auto",
    vmin=0, vmax=max(1, sector_cluster_matrix.max())
)

cbar = plt.colorbar(im, ax=ax, label="Number of Policies",
                    fraction=0.025, pad=0.03)

ax.set_xticks(range(TOP_N_CLUSTERS))
ax.set_xticklabels(col_labels, fontsize=8.0)
ax.set_yticks(range(len(unique_sectors)))
ax.set_yticklabels(row_labels, fontsize=9.0)

# Annotate only non-zero cells
for i in range(len(unique_sectors)):
    for j in range(TOP_N_CLUSTERS):
        val = sector_cluster_matrix[i, j]
        if val == 0:
            continue
        bg_intensity = val / max(1, sector_cluster_matrix.max())
        txt_color = "white" if bg_intensity > 0.55 else "#1a1a3e"
        ax.text(j, i, str(val), ha="center", va="center",
                fontsize=9, color=txt_color, fontweight="bold")

ax.set_title(
    f"Fig. 5  —  Sector \u00d7 Cluster Co-occurrence Heatmap\n"
    f"(Top {TOP_N_CLUSTERS} clusters by policy count; remaining {len(real_clusters) - TOP_N_CLUSTERS} clusters omitted)",
    pad=10
)
ax.set_xlabel("HDBSCAN Cluster ID  (n = cluster size)", labelpad=6)
ax.set_ylabel("Regulatory Sector")
fig.tight_layout()
out5 = OUTPUT_DIR / "fig5_sector_cluster_heatmap.png"
fig.savefig(out5)
plt.close(fig)
log.info(f"  Saved → {out5}")


# ═══════════════════════════════════════════════════════════════════════════════
# STEP 3 — Load recommendation scores from DB (for Figs 6-8)
# ═══════════════════════════════════════════════════════════════════════════════
#
# We query the old services.recommender (v1) which is already trained in-memory,
# since it is what evaluate_model.py uses.  We replicate that logic here so
# we don't need a live API server.
# ═══════════════════════════════════════════════════════════════════════════════

log.info("Loading recommender for score generation (Figs 6-8)...")

try:
    from app.ml.recommender_v2 import get_recommendations_v2
    log.info("Recommender ready (V2 service).")

    SECTORS_EVAL = ["AI Governance", "Cybersecurity", "Data Privacy"]

    # Pull a balanced sample: up to 10 per sector
    conn = get_connection()
    try:
        sample_rows = conn.execute(
            """
            SELECT id, sector FROM policies
            WHERE embedding IS NOT NULL
              AND sector IN ('AI Governance', 'Cybersecurity', 'Data Privacy')
            ORDER BY sector, id
            """
        ).fetchall()
    finally:
        conn.close()

    # Collect up to 10 per sector
    from collections import defaultdict
    by_sector = defaultdict(list)
    for r in sample_rows:
        if len(by_sector[r["sector"]]) < 10:
            by_sector[r["sector"]].append(r["id"])

    # ── Gather scores ──────────────────────────────────────────────────────────
    score_records = []           # {sector, score}
    country_freq  = Counter()    # total recommendation frequency
    sector_top_countries = defaultdict(set)   # for overlap matrix

    for sector, pid_list in by_sector.items():
        for pid in pid_list:
            try:
                result = get_recommendations_v2(pid, top_n=6)
                for rec in result.get("recommendations", []):
                    score_records.append({
                        "sector": sector,
                        "score": float(rec["need_score"])
                    })
                    cname = rec["country"]
                    country_freq[cname] += 1
                    sector_top_countries[sector].add(cname)
            except Exception as e:
                log.warning(f"Skipping {pid}: {e}")

    # ── FIGURE 6 — Score Distribution Box + Strip per Sector ──────────────────
    log.info("Generating Figure 6: Recommendation score distribution...")

    import pandas as pd
    df_scores = pd.DataFrame(score_records)

    fig, ax = plt.subplots(figsize=(6.5, 3.8))
    sector_order = SECTORS_EVAL
    palette_sec = {
        "AI Governance": SECTOR_COLORS["AI Governance"],
        "Cybersecurity": SECTOR_COLORS["Cybersecurity"],
        "Data Privacy":  SECTOR_COLORS["Data Privacy"],
    }

    sns.boxplot(
        data=df_scores, x="sector", y="score", order=sector_order,
        palette=palette_sec, width=0.45, linewidth=0.9,
        fliersize=0, ax=ax, zorder=2
    )
    sns.stripplot(
        data=df_scores, x="sector", y="score", order=sector_order,
        palette=palette_sec, size=3.0, alpha=0.45, jitter=0.18,
        ax=ax, zorder=3
    )

    ax.set_title("Fig. 6  —  Compatibility Score Distribution per Regulatory Sector", pad=8)
    ax.set_xlabel("Regulatory Sector")
    ax.set_ylabel("Compatibility Score  $S(C, P)$")
    ax.set_ylim(0, 1.05)
    ax.grid(axis="y", linestyle=":", zorder=0)

    # Annotate mean values
    for i, sector in enumerate(sector_order):
        vals = df_scores[df_scores["sector"] == sector]["score"]
        if len(vals):
            ax.text(i, vals.mean() + 0.025, f"μ={vals.mean():.3f}",
                    ha="center", va="bottom", fontsize=7.5, color="#333333")

    fig.tight_layout()
    out6 = OUTPUT_DIR / "fig6_score_distribution.png"
    fig.savefig(out6)
    plt.close(fig)
    log.info(f"  Saved → {out6}")


    # ── FIGURE 7 — Country Recommendation Frequency ───────────────────────────
    log.info("Generating Figure 7: Country recommendation frequency...")

    top_n_countries = 15
    top_countries = country_freq.most_common(top_n_countries)
    ctry_labels = [c[0] for c in top_countries]
    ctry_counts = [c[1] for c in top_countries]
    total_slots  = sum(ctry_counts)

    # Build a gradient from high (blue) to low (light grey)
    norm_vals = np.array(ctry_counts) / max(ctry_counts)
    bar_colors = [plt.cm.Blues(0.35 + 0.60 * v) for v in norm_vals]

    fig, ax = plt.subplots(figsize=(6.5, 5.0))
    y_pos = range(len(ctry_labels) - 1, -1, -1)  # top-to-bottom order
    bars = ax.barh(list(y_pos), ctry_counts, color=bar_colors,
                   edgecolor="white", linewidth=0.5, height=0.65)

    ax.set_yticks(list(y_pos))
    ax.set_yticklabels(ctry_labels[::-1])

    for bar, cnt, label in zip(bars, ctry_counts[::-1], ctry_labels[::-1]):
        pct = cnt / total_slots * 100
        flag = "  ⚠" if pct > 15 else ""
        ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
                f"{cnt}  ({pct:.1f}%){flag}",
                va="center", ha="left", fontsize=7.8)

    ax.set_title(f"Fig. 7  —  Top-{top_n_countries} Country Recommendation Frequency\n"
                 f"(out of {sum(ctry_counts)} total slots)", pad=8)
    ax.set_xlabel("Recommendation Count")
    ax.set_xlim(0, max(ctry_counts) * 1.40)
    ax.grid(axis="x", linestyle=":", zorder=0)
    fig.tight_layout()
    out7 = OUTPUT_DIR / "fig7_country_frequency.png"
    fig.savefig(out7)
    plt.close(fig)
    log.info(f"  Saved → {out7}")


    # ── FIGURE 8 — Cross-Sector Overlap Jaccard Matrix ────────────────────────
    log.info("Generating Figure 8: Cross-sector Jaccard overlap matrix...")

    def jaccard(set_a, set_b):
        union = set_a | set_b
        if not union:
            return 0.0
        return len(set_a & set_b) / len(union)

    overlap_matrix = np.zeros((3, 3))
    for i, s1 in enumerate(SECTORS_EVAL):
        for j, s2 in enumerate(SECTORS_EVAL):
            overlap_matrix[i, j] = jaccard(
                sector_top_countries[s1], sector_top_countries[s2]
            )

    fig, ax = plt.subplots(figsize=(4.5, 3.8))
    cmap_jac = LinearSegmentedColormap.from_list(
        "jacard_heat", ["#FFFFFF", "#F72585"], N=256
    )
    im = ax.imshow(overlap_matrix, cmap=cmap_jac, vmin=0, vmax=1, aspect="auto")
    plt.colorbar(im, ax=ax, label="Jaccard Overlap Index", fraction=0.04, pad=0.04)

    short_labels = ["AI Gov.", "Cyber", "Data Priv."]
    ax.set_xticks(range(3))
    ax.set_xticklabels(short_labels)
    ax.set_yticks(range(3))
    ax.set_yticklabels(short_labels)

    for i in range(3):
        for j in range(3):
            val = overlap_matrix[i, j]
            txt_color = "white" if val > 0.55 else "black"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center",
                    fontsize=10, color=txt_color, fontweight="bold")

    ax.set_title("Fig. 8  —  Cross-Sector Recommendation\nOverlap (Jaccard Index)", pad=8)
    fig.tight_layout()
    out8 = OUTPUT_DIR / "fig8_crosssector_overlap.png"
    fig.savefig(out8)
    plt.close(fig)
    log.info(f"  Saved → {out8}")

except ImportError as e:
    log.warning(f"Could not import recommender service: {e}")
    log.warning("Figures 6-8 skipped. Run from the 'backend' directory.")


# ═══════════════════════════════════════════════════════════════════════════════
# FINAL SUMMARY
# ═══════════════════════════════════════════════════════════════════════════════

print("\n" + "=" * 65)
print("  PAPER FIGURES GENERATED")
print("=" * 65)
for f in sorted(OUTPUT_DIR.glob("*.png")):
    size_kb = f.stat().st_size // 1024
    print(f"  {f.name:<45} {size_kb:>5} KB")
print("=" * 65)
print(f"\n  All figures saved to: {OUTPUT_DIR}\n")
