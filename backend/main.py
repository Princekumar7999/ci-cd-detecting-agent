from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import logging
import os
import shutil
from dotenv import load_dotenv

# Load .env from current directory or parent directory
load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# Import Agent Core
try:
    from backend.agent.core import build_agent_graph, AgentState
except ImportError:
    from agent.core import build_agent_graph, AgentState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://ci-cd-detecting-agent-1.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RepoRequest(BaseModel):
    repo_url: str
    team_name: str
    leader_name: str

# In-memory store for results
# Key: run_id, Value: AgentState
results_store = {}

from datetime import datetime, timezone

def get_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def run_agent_task(run_id: str, request: RepoRequest):
    logger.info(f"Starting agent run {run_id} for {request.repo_url}")
    
    workspace_dir = f"/tmp/repo_{run_id}"
    
    # Ensure clean workspace
    if os.path.exists(workspace_dir):
        shutil.rmtree(workspace_dir)
    os.makedirs(workspace_dir, exist_ok=True)
    
    start_time = results_store[run_id]["start_time"]
    
    # Initialize state
    state: AgentState = {
        "repo_url": request.repo_url,
        "team_name": request.team_name,
        "leader_name": request.leader_name,
        "workspace_dir": workspace_dir,
        "branch_name": "main", # Default branch name
        "iteration": 0,
        "max_iterations": 5, # Conform to default retry limit 5
        "lint_errors": [],
        "test_failures": [],
        "fixed_issues": [],
        "iterations_log": [],
        "start_time": start_time,
        "end_time": "",
        "status": "running"
    }
    
    # Store initial state
    results_store[run_id] = state

    # --- DEMO MODE TRIGGER ---
    if request.team_name.strip().upper() == "DEMO" or request.leader_name.strip().upper() == "DEMO":
        logger.info("DEMO MODE ACTIVATED: Simulating 60s run with specific failures.")
        import time
        
        # Simulate Analysis Phase (15s)
        time.sleep(15)
        
        # Update State: Analysis Done, Found Issues
        state["status"] = "running"
        state["iteration"] = 1
        state["lint_errors"] = [{"file": "src/utils.py", "line": 23, "type": "LINTING", "message": "Simulated error"}] # Dummy to show activity
        state["iterations_log"] = [
            {
                "iteration": 0,
                "status": "FAILED",
                "timestamp": get_utc_iso(),
                "lint_errors_count": 4,
                "test_failures_count": 0
            }
        ]
        results_store[run_id] = state
        
        # Simulate Fix Phase (15s)
        time.sleep(15)
        
        # Update State: Fixing...
        state["iteration"] = 2
        state["fixed_issues"] = [
            {
                "file": "src/validator.py", 
                "bug_type": "SYNTAX", 
                "line": 8,
                "commit_message": "SYNTAX error in src/validator.py line 8 → Fix: add the colon at the correct position", 
                "status": "Fixed"
            }
        ]
        state["iterations_log"] = state["iterations_log"] + [
            {
                "iteration": 1,
                "status": "FAILED",
                "timestamp": get_utc_iso(),
                "lint_errors_count": 3,
                "test_failures_count": 0
            }
        ]
        results_store[run_id] = state
        
        # Simulate Finalizing (30s)
        time.sleep(30)
        
        # Mock State - FINAL
        state["status"] = "completed"
        state["end_time"] = get_utc_iso()
        state["iteration"] = 3
        
        # 4 Total Failures = 0 Remaining + 4 Processed (in fixed_issues)
        state["lint_errors"] = [] 
        state["test_failures"] = []
        
        state["fixed_issues"] = [
            {
                "file": "src/validator.py", 
                "bug_type": "SYNTAX", 
                "line": 8,
                "commit_message": "SYNTAX error in src/validator.py line 8 → Fix: add the colon at the correct position", 
                "status": "Fixed"
            },
            {
                "file": "tests/test_api.py", 
                "bug_type": "SYNTAX", 
                "line": 14,
                "commit_message": "SYNTAX error in tests/test_api.py line 14 → Fix: corrected indentation block", 
                "status": "Fixed"
            },
            {
                "file": "src/utils.py", 
                "bug_type": "LINTING", 
                "line": 15,
                "commit_message": "LINTING error in src/utils.py line 15 → Fix: remove the import statement", 
                "status": "Fixed"
            },
            {
                "file": "src/config.py", 
                "bug_type": "LINTING", 
                "line": 2, 
                "commit_message": "LINTING error in src/config.py line 2 → Fix: remove the import statement", 
                "status": "Fixed"
            }
        ]
        
        state["iterations_log"] = state["iterations_log"] + [
            {
                "iteration": 2,
                "status": "PASSED",
                "timestamp": get_utc_iso(),
                "lint_errors_count": 0,
                "test_failures_count": 0
            }
        ]
        
        results_store[run_id] = state
        with open(os.path.join(workspace_dir, "results.json"), "w") as f:
            import json
            json.dump(state, f, indent=2)
        return
    # -------------------------
    
    # Build and run graph
    app_graph = build_agent_graph()
    
    try:
        # Stream the graph execution for live updates
        logger.info("Invoking agent graph with live updates...")
        for event in app_graph.stream(state):
            for node_name, node_output in event.items():
                logger.info(f"Node '{node_name}' completed.")
                if isinstance(node_output, dict):
                    state.update(node_output)
                results_store[run_id] = dict(state)
        
        # Update store with final status if not set
        if state.get("status") not in ["completed", "failed"]:
            state["status"] = "completed"
        state["end_time"] = get_utc_iso()
        results_store[run_id] = dict(state)
        
        # Write results.json
        import json
        with open(os.path.join(workspace_dir, "results.json"), "w") as f:
            json.dump(state, f, indent=2)
            
    except Exception as e:
        logger.error(f"Agent run failed: {e}", exc_info=True)
        # Rescuing state
        state["status"] = "failed"
        state["error"] = str(e)
        
        # Add a dummy failure so the dashboard shows something
        if not state.get("test_failures") and not state.get("lint_errors"):
             state["test_failures"] = [{
                 "file": "PIPELINE_ERROR",
                 "line": 0,
                 "type": "CRITICAL",
                 "message": f"Pipeline crashed: {str(e)}",
                 "test_name": "Agent Execution"
             }]
        
        results_store[run_id] = state
        
        # Try to write results.json even on failure
        try:
            # Re-create workspace_dir if it was deleted by git_ops
            os.makedirs(workspace_dir, exist_ok=True)
            import json
            with open(os.path.join(workspace_dir, "results.json"), "w") as f:
                json.dump(state, f, indent=2)
        except Exception as write_err:
            logger.error(f"Failed to write failure results: {write_err}")

@app.post("/analyze")
def analyze_repo(request: RepoRequest, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())

    results_store[run_id] = {
        "status": "pending",
        "request": request.dict(),
        "start_time": get_utc_iso(),
        "end_time": "",
        "iteration": 0,
        "lint_errors": [],
        "test_failures": [],
        "fixed_issues": [],
        "iterations_log": [],
    }

    background_tasks.add_task(run_agent_task, run_id, request)
    return {"run_id": run_id, "status": "started"}

@app.get("/results/{run_id}")
def get_results(run_id: str):
    if run_id not in results_store:
        raise HTTPException(status_code=404, detail="Run ID not found")
    return results_store[run_id]

@app.get("/status")
def health_check():
    return {"status": "ok", "service": "DevOps Agent Backend"}
