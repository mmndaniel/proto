---
name: proto
description: Idea to working prototype, fast. Collaborative planning, then autonomous parallel implementation. Use when user says "set up a project", "let's build this", "let's implement this", "continue the project", or "pick up where we left off". Do NOT use for one-off tasks, quick fixes, or conversations still exploring ideas without a decision to build.
---

# Proto

Goal: rough idea to working prototype, fast. Maximize parallelism, minimize back-and-forth.

## Detect Starting State

Check which files have content (empty files are placeholders from init):
- plan.md + progress.md have content → Phase 2
- Some files have content → Resume from next missing piece
- All empty → Phase 1

## Phase 1: Project Setup (collaborative)

Work with the user to establish these files, in this order. Confirm each before moving on.

1. **Understand the project.** If brainstorming context exists, synthesize it. If not, ask.
2. **Init repo.** Run `scripts/init-project.sh <repo-name>`
3. **PRD (prd.md).** What we're building, for whom, and why. See `references/prd-guide.md`.
4. **Architecture (architecture.md).** Stack, infrastructure, major components. Skip if obvious. See `references/architecture-guide.md`.
5. **Plan (plan.md).** Break into tasks with IDs, descriptions, and dependencies. Review with user until approved.
6. **Progress (progress.md).** All tasks pending.
7. **Update CLAUDE.md** with project file references and commit.

## Phase 2: Orchestration Loop (autonomous)

Run from inside the project directory. Worktree isolation requires a git repo in cwd.

Once the user approves the plan, run autonomously until done. Don't stop to ask unless blocked.

### Your role
You are the coordinator. You read state, delegate, and update progress. You NEVER implement code, merge branches, or run tests yourself. Always delegate to subagents. Do NOT use TaskCreate/TaskUpdate for tracking. progress.md is the tracker. Do NOT read implementation files (source code). Subagents get context from project files (prd.md, architecture.md, plan.md), not from you.

### Loop
1. **Sync.** Read progress.md and plan.md. Understand current state.
2. **Select.** Find independent pending tasks (no unmet dependencies). Batch them for parallel execution.
3. **Delegate.** Spawn one `implementer` subagent per task, ALL as parallel background agents. Use `references/subagent-prompt-template.md` for prompt structure. Give goals, not instructions. Do NOT implement anything yourself.
4. **Merge.** After all implementers finish, spawn one `integrator` subagent. Pass it the list of worktree branches (from `git worktree list`) and tell it to read plan.md for context. The integrator merges branches, resolves conflicts, runs integration checks, and cleans up worktrees.
5. **Update.** After the integrator confirms success, update progress.md with completed tasks. Update CLAUDE.md with run/test instructions as they emerge. Commit.
6. **Repeat** until all tasks are done. Then tell the user what was built.

### Handling failures

Implementers and integrators return status: done, blocked, or failed. When something goes wrong:

**Implementer returns blocked/failed:**
- Read the reason. Determine if it's a plan problem or a missing decision.
- If the task was underspecified or depends on something not yet decided: ask the user. E.g., "TASK-004 needs an auth provider but architecture.md doesn't specify one. Which do you want?"
- If the task needs restructuring (too large, wrong decomposition): update plan.md, split or rewrite the task, then re-delegate.
- Mark the task as BLOCKED in progress.md with the reason.
- Continue with other tasks that aren't affected.

**Integrator returns blocked/failed:**
- If merge conflict is unresolvable: the plan has bad task boundaries. Update plan.md to restructure conflicting tasks (e.g., combine them into one, or sequence them). Re-delegate.
- If integration tests fail: create a fix task in plan.md and delegate it to an implementer.

**Key rules:**
- NEVER fall back to implementing code yourself. If subagents fail, figure out WHY and fix the inputs (plan, architecture, task description), then re-delegate.
- When you need information that isn't in the project files (PRD, architecture, plan), ask the user. Don't guess.
- After getting user input, update the relevant project file (prd.md, architecture.md, plan.md) before re-delegating. The files are the source of truth for subagents.
