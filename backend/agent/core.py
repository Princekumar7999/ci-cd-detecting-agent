from typing import TypedDict, List, Dict, Any
import logging
import os
import git
from langgraph.graph import StateGraph, END

from .git_ops import GitOps
from .analyzer import Analyzer
from .fixer import Fixer

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    repo_url: str
    team_name: str
    leader_name: str
    workspace_dir: str
    
    iteration: int
    max_iterations: int
    
    lint_errors: List[Dict]
    test_failures: List[Dict]
    fixed_issues: List[Dict] # Log of fixes
    
    start_time: str
    end_time: str
    
    status: str # "running", "completed", "failed"

def clone_repo(state: AgentState):
    logger.info("Node: clone_repo")
    git_ops = GitOps(state["repo_url"], state["team_name"], state["leader_name"], state["workspace_dir"])
    git_ops.clone_repo()
    return {"status": "cloned", "iteration": 0}

def analyze_code(state: AgentState):
    logger.info("Node: analyze_code")
    analyzer = Analyzer(state["workspace_dir"])
    results = analyzer.analyze()
    return {
        "lint_errors": results["lint_errors"],
        "test_failures": results["test_failures"]
    }

def check_health(state: AgentState):
    logger.info("Node: check_health")
    # If no errors, we are passed
    if not state["lint_errors"] and not state["test_failures"]:
        return "passed"
    
    if state["iteration"] >= state["max_iterations"]:
        return "failed"
    
    return "fix_needed"

def apply_fix(state: AgentState):
    logger.info("Node: apply_fix")
    # Prioritize fixing: SYNTAX -> INDENTATION -> IMPORT -> TYPE_ERROR -> LOGIC -> LINTING
    # Gather all candidate errors
    candidates = []
    
    # Add lint errors
    for e in state["lint_errors"]:
        candidates.append(e)
        
    # Add test failures (usually LOGIC)
    for e in state["test_failures"]:
        # If type is not set, default to LOGIC
        if "type" not in e or e["type"] == "LOGIC":
             e["type"] = "LOGIC"
        candidates.append(e)
        
    if not candidates:
        return {"status": "completed"}
        
    # Define priority map (lower is higher priority)
    priority_map = {
        "SYNTAX": 1,
        "INDENTATION": 2,
        "IMPORT": 3,
        "TYPE_ERROR": 4,
        "LOGIC": 5,
        "LINTING": 6
    }
    
    # Sort candidates
    def get_priority(error):
        t = error.get("type", "LINTING")
        # Handle unknown types by defaulting to low priority
        return priority_map.get(t, 100)
        
    candidates.sort(key=get_priority)
    
    error_to_fix = candidates[0]
    logger.info(f"Selected error to fix: {error_to_fix['type']} in {error_to_fix['file']} (Priority: {get_priority(error_to_fix)})")
        
    if not error_to_fix:
        # Should be covered by check_health, but safety check
        return {"status": "completed"}
        
    fixer = Fixer(state["workspace_dir"])
    try:
        commit_msg = fixer.fix_error(error_to_fix)
        status = "Fixed"
    except Exception as e:
        logger.error(f"Fix failed: {e}")
        commit_msg = f"Failed to fix {error_to_fix['file']}: {str(e)}"
        status = "Failed"

    # Commit the fix
    git_ops = GitOps(state["repo_url"], state["team_name"], state["leader_name"], state["workspace_dir"])
    # Re-init git_ops is fine, it attaches to existing repo
    git_ops.repo = git.Repo(state["workspace_dir"]) 
    # Use internal gitpython method effectively
    
    if status == "Fixed":
        git_ops.commit_changes(commit_msg)
        try:
            git_ops.push_changes()
        except Exception as e:
            logger.error(f"Failed to push changes: {e}")
            status = "Fixed (Local only - Push Failed)"
            # We don't raise here, so the loop continues and we don't lose state.
            # The dashboard will show "Fixed (Local only...)"
    
    # Log the fix
    new_fix_entry = {
        "file": error_to_fix["file"],
        "bug_type": error_to_fix["type"],
        "line": error_to_fix["line"],
        "commit_message": commit_msg,
        "status": status
    }
    
    return {
        "iteration": state["iteration"] + 1,
        "fixed_issues": state["fixed_issues"] + [new_fix_entry]
    }

# Define the graph
def build_agent_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("clone_repo", clone_repo)
    workflow.add_node("analyze_code", analyze_code)
    workflow.add_node("apply_fix", apply_fix)
    
    workflow.set_entry_point("clone_repo")
    
    workflow.add_edge("clone_repo", "analyze_code")
    
    workflow.add_conditional_edges(
        "analyze_code",
        check_health,
        {
            "passed": END,
            "failed": END,
            "fix_needed": "apply_fix"
        }
    )
    
    workflow.add_edge("apply_fix", "analyze_code")
    
    return workflow.compile()
