#!/bin/bash
# Helper script to reset the sample repository back to the broken state containing the bugs

# Get the directory of this script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Resetting sample_repo back to the broken state containing the bugs..."

# Navigate to sample_repo and reset to the buggy commit
cd "${SCRIPT_DIR}/sample_repo" || { echo "Error: sample_repo directory not found!"; exit 1; }
git reset --hard 82def9b

echo "--------------------------------------------------------"
echo "Success! sample_repo is now in the buggy state."
echo "You can now run the agent with the following path:"
echo "/Users/apple/ci-cd-detecting-agent/sample_repo"
echo "--------------------------------------------------------"
