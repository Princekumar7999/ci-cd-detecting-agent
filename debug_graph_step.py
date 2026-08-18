import os
import shutil
import git
from backend.agent.core import clone_repo, analyze_code, apply_fix, check_health

# Setup initial state
repo_url = "/Users/apple/devops_agent/temp_repo" 
team_name = "TEST_TEAM"
leader_name = "TEST_LEADER"
workspace_dir = "/tmp/debug_graph_repo"

if os.path.exists(workspace_dir):
    shutil.rmtree(workspace_dir)

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

print("--- STEP 1: CLONE ---")
res_clone = clone_repo(state)
state.update(res_clone)

print("\n--- STEP 2: ANALYZE 1 ---")
res_analyze = analyze_code(state)
state.update(res_analyze)

health = check_health(state)
print(f"Health check 1: {health}")

# Fix 1
if health == "fix_needed":
    print("\n--- STEP 3: APPLY FIX 1 ---")
    res_fix = apply_fix(state)
    state.update(res_fix)

    print("\n--- STEP 4: ANALYZE 2 ---")
    res_analyze = analyze_code(state)
    state.update(res_analyze)
    
    health = check_health(state)
    print(f"Health check 2: {health}")

# Fix 2
if health == "fix_needed":
    print("\n--- STEP 5: APPLY FIX 2 ---")
    res_fix = apply_fix(state)
    state.update(res_fix)
    print(f"State after fix 2: iteration={state['iteration']}, fixed={state['fixed_issues']}")
    print("test_validator.py content after fix 2:")
    with open(os.path.join(workspace_dir, "tests/test_validator.py")) as f:
        print(f.read())

    print("\n--- STEP 6: ANALYZE 3 ---")
    res_analyze = analyze_code(state)
    state.update(res_analyze)
    print(f"Lint errors: {state['lint_errors']}")
    print(f"Test failures: {state['test_failures']}")
    
    health = check_health(state)
    print(f"Health check 3: {health}")

# Fix 3
if health == "fix_needed":
    print("\n--- STEP 7: APPLY FIX 3 ---")
    res_fix = apply_fix(state)
    state.update(res_fix)
    print(f"State after fix 3: iteration={state['iteration']}, fixed={state['fixed_issues']}")
    print("test_validator.py content after fix 3:")
    with open(os.path.join(workspace_dir, "tests/test_validator.py")) as f:
        print(f.read())

    print("\n--- STEP 8: ANALYZE 4 ---")
    res_analyze = analyze_code(state)
    state.update(res_analyze)
    print(f"Lint errors: {state['lint_errors']}")
    print(f"Test failures: {state['test_failures']}")
    
    health = check_health(state)
    print(f"Health check 4: {health}")
