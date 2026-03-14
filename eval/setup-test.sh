#!/bin/bash
# Set up a test project from a fixture for evaluation.
#
# Usage: ./setup-test.sh <fixture-name> [target-dir]
#
# Creates a git repo at target-dir with the fixture's project files
# and a CLAUDE.md pointing to proto.

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
FIXTURE="${1:?Usage: setup-test.sh <fixture-name> [target-dir]}"
FIXTURE_DIR="$SCRIPT_DIR/fixtures/$FIXTURE"
TARGET="${2:-/tmp/$FIXTURE}"

if [ ! -d "$FIXTURE_DIR" ]; then
    echo "Fixture not found: $FIXTURE_DIR"
    echo "Available fixtures:"
    ls "$SCRIPT_DIR/fixtures/"
    exit 1
fi

# Clean previous test
rm -rf "$TARGET"
mkdir -p "$TARGET"
cd "$TARGET"

git init
git branch -m main 2>/dev/null || true

# Copy fixture files
cp "$FIXTURE_DIR"/*.md .

# Add CLAUDE.md
cat > CLAUDE.md << 'EOF'
# Project Configuration

## Project Files
- `SPEC.md` - What we're building, for whom, and why.
- `ARCHITECTURE.md` - Technical decisions. Stack, components, key decisions.
- `PLAN.md` - Implementation plan. Tasks with IDs, descriptions, dependencies.
- `PROGRESS.md` - Current state. What's done, what's pending, what's blocked.

## How to work on this project
Use `/go` to plan and implement tasks.
EOF

# Add .gitignore
cat > .gitignore << 'EOF'
.env
.env.*
node_modules/
__pycache__/
*.pyc
.DS_Store
dist/
build/
.claude/worktrees/
EOF

git add -A
git commit -m "initial setup from fixture: $FIXTURE"

echo ""
echo "Test project ready at: $TARGET"
echo "To test: cd $TARGET && claude"
echo "Then say: continue the project"
