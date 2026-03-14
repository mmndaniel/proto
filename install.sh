#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

mkdir -p ~/.claude/skills ~/.claude/agents
cp -r "$SCRIPT_DIR/skills/go" ~/.claude/skills/go
cp "$SCRIPT_DIR/agents/"*.md ~/.claude/agents/

echo "Proto installed. Open Claude Code and say: /go"
