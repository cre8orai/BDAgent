#!/bin/bash
# Read the drafts waiting for you, one at a time, and approve or kill each.
#   bash agents/review.sh
#
# The prompt lives in review.py rather than a heredoc here on purpose: a heredoc
# occupies stdin, so input() would hit EOF on the first keypress.
cd "$(dirname "$0")/.." || exit 1
exec python3 agents/review.py
