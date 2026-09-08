# Published artifacts

Artifact URLs never change — anyone holding a link sees the current version on their
next load. No re-sending, no version numbers.

| Artifact | Source | Rebuilt by | URL |
|---|---|---|---|
| **Command centre** (live, David works here) | `agents/state/*.csv` | `agents/build_dashboard.py`, every run | https://claude.ai/code/artifact/a996dabf-6c6d-46ee-82a5-99a5b0e62e23 |
| Watch board (read-only, publicly shared) | superseded by the above | — | https://claude.ai/code/artifact/575aee6a-a365-4d22-a3b8-4d05c3a3cc9e |

**Why two.** The command centre declares the `db` capability so David's answers,
decisions and instructions persist and can be read back. An artifact using `db` cannot
be shared publicly, and the original board already was — so rather than silently
un-share David's link, the interactive one got its own private URL. If he turns off
public sharing on the old one, the two can be collapsed into it.

**An agent may rebuild these files. An agent may not publish them.** Publishing puts
content in front of people outside the project, and that stays with David.

`command-centre.html` is regenerated after every agent run, so the file on disk is always
current. Publishing it is the manual step — see [`agents/GATES.md`](../agents/GATES.md)
gate 6.

Related: RetailGTM publishes three of its own (pipeline, evidence base, strategy) and
the routine for all of them is in that repo's `agents/PUBLISH.md`.
