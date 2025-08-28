"""
A script for processing and visualizing game statistics data including kills, deaths,
skill, kill-death ratio, and timestamps. Outputs include statistical visualizations
and tabular data saved to PDF files.

This module provides functionality to parse game data from a CSV file, compute
kill-death ratios, generate statistical annotations for plots, and save both visual
plots and tabular data as multipage PDF documents.
"""

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
    """
    Calculates and returns the kill-death ratio based on the number of kills and
    deaths provided.

    The function computes the ratio of kills to deaths, ensuring to handle the edge
    case where deaths are zero. If the number of deaths is zero, the function will
    return the number of kills as a float.

    :param kills: The number of kills (integer).
    :param deaths: The number of deaths (integer). If zero, the ratio defaults
        to the number of kills.

    :return: The kill-death ratio as a float.
    """
    return float(kills) if deaths == 0 else (kills / deaths)


def read_game_data(file_path: str) -> Dict[str, Dict[str, float]]:
    """
    Reads game data from a CSV file and processes it into a dictionary format.

    The function extracts specific fields, including kills, deaths, skill, and
     calculates a K/D ratio, for each record, and organizes the data indexed by timestamp.

    :param file_path: The path to the CSV file containing game data
        including fields such as UTC Timestamp, Kills, Deaths, and Skill.
    :type file_path: str

    :return: A dictionary where each key is the UTC timestamp (as a string)
        and the value is another dictionary containing:
            - "Skill": The skill score as a float.
            - "Kills": The number of kills as an integer.
            - "Deaths": The number of deaths as an integer.
            - KD_LABEL: The calculated KD ratio as a float.
    :rtype: Dict[str, Dict[str, float]]
    """
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
    """
    Computes various statistical metrics for a given series of floating point numbers.

    This function calculates the minimum value, maximum value, average, span, index
    of the minimum value, and index of the maximum value in the input series.

    :param series: List of floating point numbers for which statistics are
                   computed.
    :return: A tuple containing the following:
             - Minimum value of the series
             - Maximum value of the series
             - Average value of the series
             - Span, which is the maximum of the absolute values of the
               minimum and maximum, including a small epsilon to ensure
               non-zero scaling
             - Index of the minimum value
             - Index of the maximum value
    """
    smin = min(series)
    smax = max(series)
    avg = sum(series) / len(series)
    span = max(abs(smin), abs(smax), 1e-9)
    min_idx = min(range(len(series)), key=series.__getitem__)
    max_idx = max(range(len(series)), key=series.__getitem__)
    return smin, smax, avg, span, min_idx, max_idx


def annotate_series_stats(ax, indices: List[int], series: List[float], color: str, label_prefix: str) -> None:
    """
    Annotates a plot with statistical information about a given series, including its
    minimum, maximum, and average values. The annotated values are marked and
    labeled on the given `ax`.

    :param ax: The matplotlib Axes object on which the annotations will be drawn.
    :param indices: A list of indices corresponding to data points in the series.
    :param series: A list of numerical values for which statistics are computed.
    :param color: A string representing the color of the annotations and lines.
    :param label_prefix: A string prefix used to label the annotations on the plot.

    :return: None. This function modifies the provided Axes object directly.
    """
    smin, smax, avg, span, min_idx, max_idx = compute_series_stats(series)
    ax.set_ylim(-span, span)
    ax.plot(indices[min_idx], smin, marker="o", color=color, linestyle="None", label=f"Min {label_prefix}: {smin:.2f}")
    ax.plot(indices[max_idx], smax, marker="o", color=color, linestyle="None", label=f"Max {label_prefix}: {smax:.2f}")
    ax.axhline(y=avg, color=color, linestyle="--", label=f"Avg {label_prefix}: {avg:.2f}")


def save_plot_pdf(fig, output_path: str) -> None:
    """
    Save a matplotlib figure as a PDF file in landscape orientation.

    This function saves the provided matplotlib figure to the specified output
    path in PDF format.

    :param fig: The matplotlib figure to save.
    :type fig: matplotlib.figure.Figure
    :param output_path: The path where the PDF file will be saved.
    :return: None
    """
    with PdfPages(output_path) as pdf:
        fig.set_size_inches(11, 8.5)
        pdf.savefig(orientation="landscape")
    plt.close(fig)


def save_table_pdf(game_data: Dict[str, Dict[str, float]], output_path: str) -> None:
    """
    Save a table of game data as a multipage PDF file. The table includes data such as
    timestamps, skill levels, kills, deaths, and kill-death ratios, with pagination for
    large datasets.

    :param game_data: A dictionary containing game data, where keys represent timestamps
        (as strings) and values are nested dictionaries with statistics like skill levels
        (float), kills, deaths, and kill-death ratios.
    :param output_path: The file path where the resulting PDF document should be saved.
    :return: None
    """
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
    """
    Generates a chart visualizing game statistics over time, including kill-death (KD) ratios and
    skill ratings. The chart contains dual y-axes to correlate these two metrics and provides
    annotated statistics directly on the plot for better data interpretability.

    :param game_indices: List of indices representing the sequential order of games.
                        This forms the x-axis of the chart.
    :type game_indices: list[int]
    :param kd_series: A list of kill-death ratios corresponding to each game index.
    :type kd_series: list[float]
    :param skill_series: A list of skill ratings corresponding to each game index.
    :type skill_series: list[float]
    :param timestamps_sorted: Sequential list of timestamps corresponding to each game index,
                              used to determine x-axis tick intervals.
    :type timestamps_sorted: list[str]
    :return: A Matplotlib `Figure` object representing the generated chart.
    :rtype: matplotlib.figure.Figure
    """
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
