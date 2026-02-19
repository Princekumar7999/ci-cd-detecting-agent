from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import logging
import os
import shutil
# Import Agent Core
from backend.agent.core import build_agent_graph, AgentState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

import datetime

def run_agent_task(run_id: str, request: RepoRequest):
    logger.info(f"Starting agent run {run_id} for {request.repo_url}")
    
    workspace_dir = f"/tmp/repo_{run_id}"
    
    # Ensure clean workspace
    if os.path.exists(workspace_dir):
        shutil.rmtree(workspace_dir)
    
    start_time = datetime.datetime.now().isoformat()
    
    # Initialize state
    state: AgentState = {
        "repo_url": request.repo_url,
        "team_name": request.team_name,
        "leader_name": request.leader_name,
        "workspace_dir": workspace_dir,
        "iteration": 0,
        "max_iterations": 5, 
        "lint_errors": [],
        "test_failures": [],
        "fixed_issues": [],
        "start_time": start_time,
        "end_time": "",
        "status": "running"
    }
    
    # Store initial state
    results_store[run_id] = state
    
    # Build and run graph
    app_graph = build_agent_graph()
    
    try:
        # Invoke the graph
        logger.info("Invoking agent graph...")
        final_state = app_graph.invoke(state)
        
        # Update store with final state
        final_state["status"] = "completed"
        final_state["end_time"] = datetime.datetime.now().isoformat()
        results_store[run_id] = final_state
        
        # Generator results.json
        import json
        with open(os.path.join(workspace_dir, "results.json"), "w") as f:
            json.dump(final_state, f, indent=2)
            
    except Exception as e:
        logger.error(f"Agent run failed: {e}", exc_info=True)
        # Try to rescue state if possible, or at least mark as failed
        state["status"] = "failed"
        state["error"] = str(e)
        # If e is a GraphInvocationError (langgraph), it might contain the partial state?
        # Ideally, we would want the agent to report the errors it found even if push failed.
        # But we don't have easy access to the internal graph state here if it crashed.
        # However, we can improve dashboard to show "Agent Error" instead of 0 failures.
        results_store[run_id] = state

@app.post("/analyze")
def analyze_repo(request: RepoRequest, background_tasks: BackgroundTasks):
    run_id = str(uuid.uuid4())
    # Initialize placeholder
    results_store[run_id] = {"status": "pending", "request": request.dict()}
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
