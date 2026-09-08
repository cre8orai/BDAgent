# Published artifacts

Artifact URLs never change — anyone holding a link sees the current version on their
next load. No re-sending, no version numbers.

| Artifact | Source | Rebuilt by | URL |
|---|---|---|---|
| BD Watch Board | `agents/state/*.csv` | `agents/build_dashboard.py`, every run | https://claude.ai/code/artifact/575aee6a-a365-4d22-a3b8-4d05c3a3cc9e |

**An agent may rebuild these files. An agent may not publish them.** Publishing puts
content in front of people outside the project, and that stays with David.

`pipeline.html` is regenerated after every agent run, so the file on disk is always
current. Publishing it is the manual step — see [`agents/GATES.md`](../agents/GATES.md)
gate 6.

Related: RetailGTM publishes three of its own (pipeline, evidence base, strategy) and
the routine for all of them is in that repo's `agents/PUBLISH.md`.
