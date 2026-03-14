# Plan: config-loader

## TASK-001: Config parser
Parse the config file and return a dict. Handle missing file gracefully.
Dependencies: none

## TASK-002: CLI
config_cli.py: `load <path>` prints the parsed config as JSON to stdout.
Dependencies: TASK-001
