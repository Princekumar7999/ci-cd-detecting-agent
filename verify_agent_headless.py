import os
import sys
import shutil
from backend.agent.core import build_agent_graph

# Mocking the request
repo_url = "/Users/apple/devops_agent/temp_repo" 
team_name = "TEST_TEAM"
leader_name = "TEST_LEADER"

# Clean previous run
workspace_dir = "/tmp/test_run_repo"
if os.path.exists(workspace_dir):
    shutil.rmtree(workspace_dir)

# Initial state
state = {
    "repo_url": repo_url,
    "team_name": team_name,
    "leader_name": leader_name,
    "workspace_dir": workspace_dir,
    "iteration": 0,
    "max_iterations": 3,
    "lint_errors": [],
    "test_failures": [],
    "fixed_issues": [],
    "start_time": "2023-01-01T00:00:00",
    "end_time": "",
    "status": "running"
}

print("Starting Headless Agent Test...")
graph = build_agent_graph()
final_state = graph.invoke(state)

print(f"Final Status: {final_state['status']}")
print(f"Fixed Issues: {len(final_state['fixed_issues'])}")
for fix in final_state['fixed_issues']:
    print(f" - Fixed {fix['bug_type']} in {fix['file']}")

if final_state['status'] == 'completed' and not final_state['lint_errors'] and not final_state['test_failures']:
    print("SUCCESS: Agent repaired the repository!")
    sys.exit(0)
else:
    print("FAILURE: Agent did not repair the repository.")
    print(f"Remaining Lint Errors: {len(final_state['lint_errors'])}")
    print(f"Remaining Test Failures: {len(final_state['test_failures'])}")
    sys.exit(1)
