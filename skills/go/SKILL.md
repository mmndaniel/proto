---
name: go
description: Idea to working prototype. Structured planning, then implementation. Use when user says "set up a project", "let's build", "let's start a project", "continue the project", or "pick up where we left off". Do NOT use for one-off tasks, quick fixes, or conversations still exploring ideas without a decision to build.
---

# Proto

Goal: rough idea to working prototype, fast.

## Detect Starting State

Check which files have content (empty files are placeholders from init):
- PLAN.md + PROGRESS.md have content → Phase 2
- Some files have content → Resume from next missing piece
- All empty → Phase 1

## Phase 1: Project Setup (collaborative)

Work with the user to establish these files, in this order. Confirm each before moving on.

1. **Understand the project.** If brainstorming context exists, synthesize it. If not, ask.
2. **Init repo.** Run `scripts/init-project.sh <repo-name>`
3. **SPEC.md.** What we're building, for whom, and why. See `references/spec-guide.md`.
4. **ARCHITECTURE.md.** Stack, infrastructure, major components. Skip if obvious. See `references/architecture-guide.md`.
5. **PLAN.md.** Break into tasks with IDs, descriptions, and dependencies. Review with user until approved.
6. **PROGRESS.md.** All tasks pending.
7. **Update CLAUDE.md** with project file references and commit.

## Phase 2: Implementation

Once the user approves the plan, work through it autonomously. Update PROGRESS.md after completing each task. Update CLAUDE.md with run/test instructions as they emerge. Commit after each batch of work.

By default, delegate tasks to `implementer` subagents in parallel as background agents. Each runs in an isolated git worktree and auto-commits. After a batch finishes, use the `integrator` subagent to merge branches and run integration checks. This keeps implementation out of the main context.

If `init-project.sh` output contained "Git repo created mid-session", subagent worktrees will not work in this session. Tell the user: "The plan is ready. Start a new session and say 'continue the project' for parallel subagents, or I can implement directly here." If the user chooses to continue, implement directly in the main context.

If the user asks to implement directly (e.g., "just do it here", "no subagents"), implement in the main context instead.

### Handling failures

When something is blocked or fails:

- If a task is underspecified or depends on an undecided architecture choice: ask the user. E.g., "TASK-004 needs an auth provider but ARCHITECTURE.md doesn't specify one. Which do you want?"
- If a task needs restructuring (too large, wrong decomposition): update PLAN.md, split or rewrite the task.
- Mark blocked tasks as BLOCKED in PROGRESS.md with the reason. Continue with unaffected tasks.
- When you need information that isn't in the project files, ask the user. Don't guess.
- After getting user input, update the relevant project file before continuing. The files are the source of truth.
