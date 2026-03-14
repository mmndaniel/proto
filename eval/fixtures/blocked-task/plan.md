# Plan: price-checker

## TASK-001: API client
Fetch prices from the internal pricing API. Return list of dicts with product, price, currency fields.
Dependencies: none

## TASK-002: CLI display
price_cli.py: `check` fetches prices and prints a formatted table to stdout.
Dependencies: TASK-001
