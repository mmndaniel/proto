#!/bin/bash
# Test Phase 1 (new project setup) by scripting a multi-turn conversation.
# Simulates: user describes idea -> SPEC -> architecture -> plan -> approve -> implement
#
# Usage: ./run-new-project.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results/$(date +%Y%m%d-%H%M%S)-new-project"
TARGET="/tmp/proto-eval-new-project"
mkdir -p "$RESULTS_DIR"

echo "============================================"
echo "PROTO EVAL: NEW PROJECT (Phase 1 + 2)"
echo "============================================"

# Clean slate
rm -rf "$TARGET"
mkdir -p "$TARGET"
cd "$TARGET"
git init && git branch -m main 2>/dev/null

# Turn 1: Describe the idea
echo "[1/5] Describing the idea..."
claude \
    --dangerously-skip-permissions \
    --plugin-dir "$PLUGIN_DIR" \
    -p "let's build a todo list CLI in Python. Simple: add tasks, list them, mark done, delete. Store in a JSON file at ~/.todos.json. No dependencies, stdlib only." \
    > "$RESULTS_DIR/turn1-idea.txt" 2>&1 || true

# Turn 2: Approve PRD and architecture
echo "[2/5] Approving PRD and architecture..."
claude \
    --dangerously-skip-permissions \
    --plugin-dir "$PLUGIN_DIR" \
    --continue \
    -p "Looks good. Approve the spec and architecture. Let's move to the plan." \
    > "$RESULTS_DIR/turn2-approve-prd.txt" 2>&1 || true

# Turn 3: Approve plan
echo "[3/5] Approving the plan..."
claude \
    --dangerously-skip-permissions \
    --plugin-dir "$PLUGIN_DIR" \
    --continue \
    -p "Plan looks good. Approve it and start implementing." \
    > "$RESULTS_DIR/turn3-approve-plan.txt" 2>&1 || true

# Turn 4: If it's still asking, tell it to go
echo "[4/5] Ensuring implementation starts..."
claude \
    --dangerously-skip-permissions \
    --plugin-dir "$PLUGIN_DIR" \
    --continue \
    -p "Yes, go ahead and implement everything." \
    > "$RESULTS_DIR/turn4-implement.txt" 2>&1 || true

# Check what files were created
echo "[5/5] Checking results..."
echo "Files created:" > "$RESULTS_DIR/summary.txt"
find "$TARGET" -type f -not -path '*/.git/*' -not -path '*/.claude/*' | sort >> "$RESULTS_DIR/summary.txt"
echo "" >> "$RESULTS_DIR/summary.txt"

# Check for project files
for f in SPEC.md ARCHITECTURE.md PLAN.md PROGRESS.md CLAUDE.md; do
    if [ -f "$TARGET/$f" ]; then
        echo "  [+] $f exists" >> "$RESULTS_DIR/summary.txt"
    else
        echo "  [X] $f MISSING" >> "$RESULTS_DIR/summary.txt"
    fi
done

# Check progress
if [ -f "$TARGET/PROGRESS.md" ]; then
    echo "" >> "$RESULTS_DIR/summary.txt"
    echo "Progress:" >> "$RESULTS_DIR/summary.txt"
    cat "$TARGET/PROGRESS.md" >> "$RESULTS_DIR/summary.txt"
fi

# Run eval on the session
PROJECT_KEY=$(echo "$TARGET" | sed 's|/|-|g')
SESSION_DIR="$HOME/.claude/projects/$PROJECT_KEY"
LATEST_SESSION=$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1)

if [ -n "$LATEST_SESSION" ]; then
    python3 "$SCRIPT_DIR/measure-session.py" "$LATEST_SESSION" > "$RESULTS_DIR/eval.txt" 2>&1
    echo ""
    cat "$RESULTS_DIR/eval.txt"
fi

echo ""
cat "$RESULTS_DIR/summary.txt"
echo ""
echo "Results saved to: $RESULTS_DIR"
