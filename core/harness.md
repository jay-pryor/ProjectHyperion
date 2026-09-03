---
id: CORE-HRN-001
title: Harness Binding
tier: core
status: active
audience: [human, model]
load: on-task
sessions: [GATE, CONTRACT, CONFORMANCE, IMPLEMENT, REVIEW, INTEGRATE, LESSON, BASELINE, QUERY, FRAMEWORK]
prevents: Session rules staying honour-based when the runtime could deny the write, pin the model, and withhold the tool
reader: A session wondering why a write was denied, and a FRAMEWORK session changing the binding
related: [CORE-SES-001, CORE-REV-001, CORE-REV-003, CORE-TRC-002, CORE-TRC-003, CORE-IMP-001, CORE-PRN-001, AGT-000, TOOL-001]
---

# Harness Binding

Every session runs inside a runtime that can withhold tools, deny writes, pin models,
and start a subagent with a prompt of its own. Left unused, every rule in
[CORE-SES-001](session-protocol.md) stays honour-based when it could be a check
([P2](00-principles.md)). This document says what a binding to that runtime must
provide and what it cannot. Read by any session that wonders why a write was denied,
and by FRAMEWORK sessions changing the binding.

## What a binding provides

Rendered by `build_layer.py` from the sources named, never written by hand
([P3](00-principles.md)); `init_project.py` and `--upgrade` render a project's copy.

| Piece | What it enforces | Source |
|---|---|---|
| One skill per session type (`/implement SL-nn <scope>`) | Prints the declaration, which the scope hook binds to this session's id, lists exactly the loadout, the may and must-not sets, the stop conditions; waits unless the type does not | session-types block, frontmatter `sessions:`, the fragments |
| One agent per lens | Read-only tools, model pinned, prompt and inputs verbatim from the agent file, told to disregard project instructions other than the read-only restriction | `agents/*.md` |
| The scope hook | Denies an `Edit`, `Write`, `MultiEdit` or `NotebookEdit` outside the declared type's globs before it happens, and denies any `Bash` that can write at all; inside a lens agent denies every write but `trace/findings.yaml` and every command but the test command | `.hyperion/session-types.json` |
| The session-start check | Warns, never blocks, when a plugin outside the declared list is enabled | `.claude/settings.json` |
| The settings file | The two hooks and `enabledPlugins`, the union of the chosen profiles' `plugins` lists | `profiles/*/fragment.yaml` |
| The container | The same toolchain in every Codespace | `tooling/claude-code/devcontainer.json` |
| The review fan-out (`/review SL-nn [lens ...]`) | Assembles the permitted inputs mechanically, runs the lenses as parallel subagents, appends their findings; fixes nothing ([P9](00-principles.md)) | the slice record and definition, `agents/*.md` |

The fan-out is the only orchestration the binding provides. No model orchestrates
sessions: if unattended chaining is ever wanted it is a script running headless sessions
in order, each with its own tool set and model, not an agent making rulings
([P10](00-principles.md)).

## Limits the runtime cannot remove

**A shell command's paths are not visible to a hook.** No parse of one is sound; a
quoting trick reaches any path. So the hook denies `Bash` whenever it can write —
a redirection, a file-mutating command, an in-place stream editor, a program handed to
an interpreter inline — rather than guessing where the write lands, and writes go
through the tools whose path is a field it can read. What stays allowed is reading and
running a program that is checked in. What that program writes, and what `git` moves,
is visible only in the diff: `check_commit.py` over the real paths of each commit is
the layer that sees it, which is why it runs on every push and not only on pull
requests.

**A subagent is only as clean as the prompt its parent wrote.** The parent chooses what
the child sees, so separation between two contexts cannot be delegated to a third that
holds both. CONFORMANCE and IMPLEMENT are therefore top-level sessions, never spawned
from one another and never spawned from inside any subagent ([P8](00-principles.md)).

**No priming stays honour-based at one point.** The fan-out passes only what each lens's
permitted-inputs section names, and nothing the human typed after the lens names; what
the human types there is the residue the protocol already accepts
([CORE-REV-003](reviews/lens-reviews.md)). A subagent also receives the project
`CLAUDE.md`; the agent definition tells it to disregard everything there except the
read-only restriction, which is why that restriction is in the definition, not only in
the hook.

## Plugins the framework excludes

The declared list is versioned with the project and arrives with the Codespace; a plugin
outside it is a warning from the session-start check, not a prohibition. Toolchain
plugins (language servers) are declared by a profile when its toolchain decision is
made, never in advance ([P6](00-principles.md)). Excluded outright, with the principle
each violates:

| Class | Why |
|---|---|
| Writes `CLAUDE.md` or trace records | Both are generated or session-written; a second writer is a second source ([P3](00-principles.md)) |
| Carries memory across sessions | Context separation is the only control against contamination ([P8](00-principles.md)) |
| Authors tests and implementation in one session | The suite is shaped around the implementation ([P8](00-principles.md)) |
| Overrides stop conditions or makes rulings for the human | The human owns the problem ([P10](00-principles.md)) |

## Model independence

A model reviewing its own family's output shares its blind spots
([CORE-REV-001](reviews/00-review-taxonomy.md)). Choosing a different model is the
cheapest partial closure, so review agents default to a different family from the
authoring session, per agent in the `model:` field ([TOOL-001](../tooling/doc-frontmatter-schema.md)):
gate and specification review on `opus`, verification and the lenses on `sonnet`. The
authoring session's model is what these must differ from; a slice records it in
`authored_by` ([CORE-TRC-002](traceability/trace-records.md)), and a review's `reviewer`
names the model that ran it as well as the person ([CORE-TRC-003](traceability/trace-logs.md)).
`check_traces.py` warns when a gate or specification review names no model, and fails
when a gate, specification, or lens review ran on the slice's authoring model. Which
model suits which lens is calibration data from the rejected-findings list, not a rule.

## One binding

`tooling/claude-code/` binds Claude Code, written from what this repository uses. Another
binding is written only when a real project needs it, under the rule that forbids
speculative profiles (HYP-002). The rendered outputs are `.claude/` (skills, agents,
hooks, settings), `.hyperion/session-types.json`, and `.devcontainer/`, in this
repository and in every project; `build_layer.py --check` fails CI when any is stale.

A declared type is bound to the runtime's session id, at `.hyperion/sessions/<id>`,
written by the hook when it sees a declaration go past and never by the session itself: a
session that could restate its own type could widen it. Keying it to the working tree
instead would let a second session in the same tree overwrite the first's scope, and let
a session that declared nothing inherit yesterday's — always in the permissive direction,
so the hook would authorise rather than fail to deny. A session with no binding of its
own is undeclared, warned once, and unrestricted. Bindings are scratch state, aged out
after a week, and ignored by git.
