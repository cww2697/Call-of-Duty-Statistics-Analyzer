# Call of Duty Statistics Analyzer

Transform your Call of Duty gameplay data into insightful visual reports with this Python analyzer. This application
processes performance statistics from CSV files to generate detailed graphs and tables showing your Skill Rating
progression, Kills per Match, Deaths per Match, and K/D ratio trends over time. Import your stats by copying the
desired multiplayer statistics table from your Activision Data Request HTML file into a CSV format.

## Installation

1. Ensure Python 3.x is installed on your system
2. Clone this repository
3. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
4. Activate the virtual environment:
    - Windows:
      ```bash
      .venv\Scripts\activate
      ```
    - Unix/MacOS:
      ```bash
      source .venv/bin/activate
      ```
5. Install required packages:
   ```bash
   pip install matplotlib
   ```

## Usage

1. Activate the virtual environment (see above)
2. Run the program:
   ```bash
   python cod_stats.py
   ```
3. When prompted, enter the path to your CSV file containing game statistics

## Input Data Format

The CSV file should contain the following columns:

- UTC Timestamp
- Skill (float)
- Kills (integer)
- Deaths (integer)

## Output

The program generates two PDF files in the `output` directory:

1. `game_statistics_graph.pdf` - A graph showing K/D ratio and skill trends over time
2. `game_statistics_data.pdf` - A tabular representation of the game data

Features:

- Automatic calculation of K/D ratios
- Statistical analysis (min, max, average)
- Multi-page table support for large datasets
- Professional-grade visualizations


