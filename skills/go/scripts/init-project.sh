#!/bin/bash
set -e

PROJECT_NAME="${1:?Usage: init-project.sh <project-name>}"
PROJECT_DIR="${2:-./$PROJECT_NAME}"

if [ ! -d "$PROJECT_DIR" ]; then
    mkdir -p "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"

if [ ! -d ".git" ]; then
    git init
    echo -e "\033[1;33mNOTE: Git repo created mid-session. Restart Claude Code for subagent worktrees to work.\033[0m"
fi

# Create all project files as empty placeholders
touch SPEC.md
touch ARCHITECTURE.md
touch PLAN.md
touch PROGRESS.md

# CLAUDE.md - the README for agents
if [ ! -f "CLAUDE.md" ]; then
    cat > CLAUDE.md << 'CLAUDE_EOF'
# Project Configuration

## Project Files
- `SPEC.md` - What we're building, for whom, and why.
- `ARCHITECTURE.md` - Technical decisions. Stack, components, key decisions.
- `PLAN.md` - Implementation plan. Tasks with IDs, descriptions, dependencies.
- `PROGRESS.md` - Current state. What's done, what's pending, what's blocked.

## How to work on this project
Use `/go` to plan and implement tasks.
CLAUDE_EOF
fi

if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'GITIGNORE_EOF'
.env
.env.*
node_modules/
__pycache__/
*.pyc
.DS_Store
dist/
build/
.claude/worktrees/
GITIGNORE_EOF
fi

echo "Project '$PROJECT_NAME' initialized at $PROJECT_DIR"
