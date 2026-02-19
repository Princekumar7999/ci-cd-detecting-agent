import os
import git
import shutil
from typing import Optional

class GitOps:
    def __init__(self, repo_url: str, team_name: str, leader_name: str, workspace_dir: str = "/tmp/repo"):
        self.repo_url = repo_url
        self.team_name = team_name.strip().upper().replace(" ", "_")
        self.leader_name = leader_name.strip().upper().replace(" ", "_")
        self.branch_name = f"{self.team_name}_{self.leader_name}_AI_Fix"
        self.workspace_dir = workspace_dir
        self.repo: Optional[git.Repo] = None

    def clone_repo(self):
        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir)
        
        print(f"Cloning {self.repo_url} to {self.workspace_dir}...")
        self.repo = git.Repo.clone_from(self.repo_url, self.workspace_dir)
        
        print(f"Checking out branch {self.branch_name}...")
        # Create and checkout new branch
        try:
            self.repo.git.checkout("-b", self.branch_name)
        except git.GitCommandError:
            self.repo.git.checkout(self.branch_name)

    def commit_changes(self, message: str):
        if not self.repo:
            raise Exception("Repository not cloned")
        
        # Check if there are changes
        if not self.repo.is_dirty(untracked_files=True):
            print("No changes to commit.")
            return

        print(f"Committing changes: {message}")
        self.repo.git.add(A=True)
        self.repo.index.commit(f"[AI-AGENT] {message}")

    def push_changes(self):
        if not self.repo:
            raise Exception("Repository not cloned")
        
        print(f"Pushing changes to {self.branch_name}...")
        origin = self.repo.remote(name="origin")
        # Set upstream to handle new branch push
        
        # Retry logic for push
        max_retries = 3
        import time
        for i in range(max_retries):
            try:
                self.repo.git.push("--set-upstream", "origin", self.branch_name)
                print("Push successful.")
                return
            except git.GitCommandError as e:
                print(f"Push failed (attempt {i+1}/{max_retries}): {e}")
                if i < max_retries - 1:
                    time.sleep(5) # Wait 5 seconds before retry
                else:
                    raise e
