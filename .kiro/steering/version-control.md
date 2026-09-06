# Version Control Rule

## 🚨 NEVER Commit on the User's Behalf — Ever

The agent MUST NEVER create a commit. This is an absolute, non-negotiable rule.

**The agent is FORBIDDEN from running any of these commands, even if explicitly
asked:**
- `git commit` (including `--amend`, `--no-verify`, `-m`, etc.)
- `git push`
- `git merge`, `git rebase`
- `git reset --hard`, `git revert`
- `git cherry-pick`
- `git tag`
- Any alias, script, or Makefile target that performs a commit/push
- Any pre-commit/CI command whose purpose is to produce a commit

**Committing is exclusively the user's responsibility.** The user decides what,
when, and how to commit. The agent never does it for them.

## What the Agent MAY Do

Read-only git inspection is allowed and encouraged when helpful:
- `git status`
- `git diff` / `git diff --staged`
- `git log`, `git show`
- `git branch` (listing only)

The agent may also **help prepare** a commit without performing it:
- Draft a commit message as text in the chat for the user to copy
- Summarize the changes that are staged/unstaged
- Explain which files changed and why

## If the User Says "commit this"

Do NOT run the commit. Instead:
1. Show the changes (`git status` / `git diff`) so the user can review.
2. Provide a suggested commit message as text.
3. Tell the user to run the commit themselves.

Example response: "Here's a suggested message — run it yourself when ready:
`git commit -m \"...\"`. I won't commit on your behalf."

## Why This Matters

- The user maintains full control and authorship over their history.
- Commits are intentional checkpoints the user owns.
- Prevents accidental commits of secrets, unrelated changes, or unreviewed code.

## Red Flags

🚩 Any use of `git commit`, `git push`, or `git amend` by the agent
🚩 A Makefile target or script that commits/pushes being run by the agent
🚩 Interpreting "save my work" or "commit this" as permission to commit — it is not
