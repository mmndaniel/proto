# Plan: statslib

## TASK-001: Data loader
loader.py: `load_csv(path)` reads a CSV file. Returns a dict mapping column names to lists of float values. Use csv.DictReader.
Dependencies: none

## TASK-002: Stats calculator
stats.py: `compute_stats(values)` takes a list of numbers and returns a dict with keys "mean", "median", "stddev". Also: `summarize(data)` takes the output of the data loader and returns stats for each column. Include a `if __name__ == "__main__"` block that loads a CSV from sys.argv[1] and prints stats for all columns.
Dependencies: none
