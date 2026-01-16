#!/bin/bash
# Wrapper script for constraint validation hook
# All output goes to log file, nothing to stdout/stderr
python3 archive/scripts/validate_constraint_reference.py >> ~/.claude/hook.log 2>&1
exit 0
