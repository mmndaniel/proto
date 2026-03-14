#!/bin/bash
# Run the full eval suite: set up each fixture, run proto, measure results.
#
# Usage: ./run-suite.sh [fixture-name]
#   No args = run all fixtures
#   With arg = run only that fixture
#
# Requires: claude CLI in PATH

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PLUGIN_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
RESULTS_DIR="$SCRIPT_DIR/results/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$RESULTS_DIR"

# Which fixtures to run
if [ -n "$1" ]; then
    FIXTURES=("$1")
else
    FIXTURES=($(ls "$SCRIPT_DIR/fixtures/"))
fi

echo "============================================"
echo "PROTO EVAL SUITE"
echo "============================================"
echo "Plugin:   $PLUGIN_DIR"
echo "Results:  $RESULTS_DIR"
echo "Fixtures: ${FIXTURES[*]}"
echo ""

for fixture in "${FIXTURES[@]}"; do
    echo "--------------------------------------------"
    echo "FIXTURE: $fixture"
    echo "--------------------------------------------"

    TARGET="/tmp/proto-eval-$fixture"

    # Set up test project
    echo "[1/3] Setting up test project..."
    bash "$SCRIPT_DIR/setup-test.sh" "$fixture" "$TARGET" > /dev/null 2>&1

    # Run claude
    echo "[2/3] Running proto (this may take a few minutes)..."
    cd "$TARGET"
    claude \
        --dangerously-skip-permissions \
        --plugin-dir "$PLUGIN_DIR" \
        -p "continue the project" \
        > "$RESULTS_DIR/$fixture-output.txt" 2>&1 || true

    # Find the session transcript
    # Claude Code stores projects with leading dash: /tmp/foo -> -tmp-foo
    PROJECT_KEY=$(echo "$TARGET" | sed 's|/|-|g')
    SESSION_DIR="$HOME/.claude/projects/$PROJECT_KEY"
    LATEST_SESSION=$(ls -t "$SESSION_DIR"/*.jsonl 2>/dev/null | head -1)

    if [ -z "$LATEST_SESSION" ]; then
        echo "[!] No session transcript found for $fixture"
        echo "SKIP" > "$RESULTS_DIR/$fixture-eval.txt"
        continue
    fi

    # Run eval
    echo "[3/3] Measuring..."
    python3 "$SCRIPT_DIR/measure-session.py" "$LATEST_SESSION" > "$RESULTS_DIR/$fixture-eval.txt" 2>&1

    # Print summary
    echo ""
    cat "$RESULTS_DIR/$fixture-eval.txt"
    echo ""

    # Copy session transcript for debugging
    cp "$LATEST_SESSION" "$RESULTS_DIR/$fixture-session.jsonl" 2>/dev/null || true

    # Copy subagent transcripts
    SESSION_ID=$(basename "$LATEST_SESSION" .jsonl)
    if [ -d "$SESSION_DIR/$SESSION_ID/subagents" ]; then
        mkdir -p "$RESULTS_DIR/$fixture-subagents"
        cp "$SESSION_DIR/$SESSION_ID/subagents"/*.jsonl "$RESULTS_DIR/$fixture-subagents/" 2>/dev/null || true
        cp "$SESSION_DIR/$SESSION_ID/subagents"/*.meta.json "$RESULTS_DIR/$fixture-subagents/" 2>/dev/null || true
    fi
done

echo ""
echo "============================================"
echo "SUITE COMPLETE"
echo "============================================"
echo "Results saved to: $RESULTS_DIR"
echo ""
echo "Quick summary:"
for fixture in "${FIXTURES[@]}"; do
    eval_file="$RESULTS_DIR/$fixture-eval.txt"
    if [ -f "$eval_file" ]; then
        passes=$(grep -c "PASS" "$eval_file" 2>/dev/null || echo 0)
        fails=$(grep -c "FAIL" "$eval_file" 2>/dev/null || echo 0)
        warns=$(grep -c "WARN" "$eval_file" 2>/dev/null || echo 0)
        active=$(grep "Active time" "$eval_file" 2>/dev/null | awk '{print $NF}')
        printf "  %-20s PASS:%s FAIL:%s WARN:%s  Active: %s\n" "$fixture" "$passes" "$fails" "$warns" "$active"
    else
        printf "  %-20s SKIPPED\n" "$fixture"
    fi
done
