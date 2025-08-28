import os
import csv
from typing import Dict, List, Tuple
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


OUTPUT_DIR = "output"
GRAPH_PDF_NAME = "game_statistics_graph.pdf"
TABLE_PDF_NAME = "game_statistics_data.pdf"
KD_LABEL = "K/D Ratio"
SKILL_LABEL = "Skill"
KD_COLOR = "cornflowerblue"
SKILL_COLOR = "indianred"
XTICK_STEP = 25
ROWS_PER_PAGE = 40
TABLE_HEADERS = ["Timestamp", "Skill", "Kills", "Deaths", "K/D Ratio"]


def parse_kd_ratio(kills: int, deaths: int) -> float:
    return float(kills) if deaths == 0 else (kills / deaths)


def read_game_data(file_path: str) -> Dict[str, Dict[str, float]]:
    game_data: Dict[str, Dict[str, float]] = {}
    with open(file_path, "r", encoding="utf-8") as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            # Handle potential BOM in header name
            ts = row.get("﻿UTC Timestamp") or row.get("UTC Timestamp")
            if not ts:
                continue
            kills = int(row["Kills"])
            deaths = int(row["Deaths"])
            skill = float(row["Skill"])
            game_data[ts] = {
                "Skill": skill,
                "Kills": kills,
                "Deaths": deaths,
                KD_LABEL: parse_kd_ratio(kills, deaths),
            }
    return game_data


def compute_series_stats(series: List[float]) -> Tuple[float, float, float, float, int, int]:
    smin = min(series)
    smax = max(series)
    avg = sum(series) / len(series)
    span = max(abs(smin), abs(smax), 1e-9)
    min_idx = min(range(len(series)), key=series.__getitem__)
    max_idx = max(range(len(series)), key=series.__getitem__)
    return smin, smax, avg, span, min_idx, max_idx


def annotate_series_stats(ax, indices: List[int], series: List[float], color: str, label_prefix: str) -> None:
    smin, smax, avg, span, min_idx, max_idx = compute_series_stats(series)
    ax.set_ylim(-span, span)
    ax.plot(indices[min_idx], smin, marker="o", color=color, linestyle="None", label=f"Min {label_prefix}: {smin:.2f}")
    ax.plot(indices[max_idx], smax, marker="o", color=color, linestyle="None", label=f"Max {label_prefix}: {smax:.2f}")
    ax.axhline(y=avg, color=color, linestyle="--", label=f"Avg {label_prefix}: {avg:.2f}")


def save_plot_pdf(fig, output_path: str) -> None:
    with PdfPages(output_path) as pdf:
        fig.set_size_inches(11, 8.5)
        pdf.savefig(orientation="landscape")
    plt.close(fig)


def save_table_pdf(game_data: Dict[str, Dict[str, float]], output_path: str) -> None:
    data_rows = list(sorted(game_data.keys()))
    total_pages = (len(data_rows) + ROWS_PER_PAGE - 1) // ROWS_PER_PAGE
    for page in range(total_pages):
        fig, ax = plt.subplots(figsize=(8.5, 11))
        ax.axis("off")
        plt.title(f"Game Data Table - Page {page + 1} of {total_pages}", pad=20)
        start_idx = page * ROWS_PER_PAGE
        end_idx = min((page + 1) * ROWS_PER_PAGE, len(data_rows))
        current_rows = data_rows[start_idx:end_idx]
        table_data: List[List[str]] = [TABLE_HEADERS]
        for timestamp in current_rows:
            data = game_data[timestamp]
            row = [
                timestamp,
                f"{data['Skill']:.2f}",
                str(data["Kills"]),
                str(data["Deaths"]),
                f"{data[KD_LABEL]:.2f}",
            ]
            table_data.append(row)


        table = ax.table(cellText=table_data, loc="center", cellLoc="center", bbox=[0.1, 0.1, 0.8, 0.8])
        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1.2, 1.5)
        col_widths = [0.3, 0.15, 0.15, 0.15, 0.15]
        for i, width in enumerate(col_widths):
            for cell in table._cells:
                if cell[1] == i:
                    table._cells[cell].set_width(width)
        with PdfPages(output_path) as pdf:
            pdf.savefig(fig)
        plt.close(fig)


def generate_chart(game_indices, kd_series, skill_series, timestamps_sorted):
    fig, ax1 = plt.subplots(figsize=(12, 6))
    ax1.set_xlabel("Game Number")
    ax1.set_ylabel(KD_LABEL, color=KD_COLOR)
    ax1.plot(game_indices, kd_series, color=KD_COLOR, linestyle="-", label=KD_LABEL)
    ax1.tick_params(axis="y", labelcolor=KD_COLOR, length=4, width=1, direction="inout")
    ax1.spines["left"].set_position(("data", 0))
    ax2 = ax1.twinx()
    ax2.set_ylabel(SKILL_LABEL, color=SKILL_COLOR)
    ax2.plot(game_indices, skill_series, color=SKILL_COLOR, linestyle="-", label=SKILL_LABEL)
    ax2.tick_params(axis="y", labelcolor=SKILL_COLOR, length=4, width=1, direction="inout")
    ax2.spines["left"].set_position(("data", 0))
    if kd_series:
        annotate_series_stats(ax1, game_indices, kd_series, KD_COLOR, KD_LABEL)
    if skill_series:
        annotate_series_stats(ax2, game_indices, skill_series, SKILL_COLOR, SKILL_LABEL)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(
        lines1 + lines2,
        labels1 + labels2,
        loc="upper right",
        fancybox=True,
        bbox_to_anchor=(1.0, 1.0),
        framealpha=1.0,
        facecolor="white",
        edgecolor="black",
        bbox_transform=ax1.transAxes,
    )
    plt.title("Game Statistics Over Time")
    plt.grid(True, axis="x")
    xticks = range(1, len(timestamps_sorted) + 1, XTICK_STEP)
    plt.xticks(xticks)
    plt.tick_params(axis="x", direction="inout")
    plt.tight_layout()
    return fig


def main():
    file_path = input("Enter file path: ").strip('"\'')
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    game_data = read_game_data(file_path)
    if not game_data:
        print("No valid data found in the CSV.")
        return

    timestamps_sorted = sorted(game_data.keys())
    kd_series = [game_data[ts][KD_LABEL] for ts in timestamps_sorted]
    skill_series = [game_data[ts][SKILL_LABEL] for ts in timestamps_sorted]
    game_indices = list(range(1, len(timestamps_sorted) + 1))

    fig = generate_chart(game_indices, kd_series, skill_series, timestamps_sorted)

    graph_pdf_path = os.path.join(OUTPUT_DIR, GRAPH_PDF_NAME)
    save_plot_pdf(fig, graph_pdf_path)

    table_pdf_path = os.path.join(OUTPUT_DIR, TABLE_PDF_NAME)
    save_table_pdf(game_data, table_pdf_path)

    print(f"PDF saved as {graph_pdf_path}")


if __name__ == "__main__":
    main()
