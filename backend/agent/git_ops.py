import os
import git
import shutil
import logging
from typing import Optional
from dotenv import load_dotenv

load_dotenv()
load_dotenv(os.path.join(os.path.dirname(__file__), "../..", ".env"))

logger = logging.getLogger(__name__)

class GitOps:
    def __init__(self, repo_url: str, team_name: str, leader_name: str, workspace_dir: str = "/tmp/repo"):
        import re
        url = repo_url.strip()
        if url and not url.startswith("http://") and not url.startswith("https://") and not url.startswith("git@"):
            url = f"https://github.com/{url}"
        self.team_name = re.sub(r'[^A-Z0-9_]', '', team_name.strip().upper().replace(" ", "_"))
        self.leader_name = re.sub(r'[^A-Z0-9_]', '', leader_name.strip().upper().replace(" ", "_"))
        # Branch name created directly from Name / Team Name input
        clean_branch = re.sub(r'[^a-zA-Z0-9_-]', '_', team_name.strip()).strip('_')
        self.branch_name = clean_branch if clean_branch else "ai_agent_fix"
        self.workspace_dir = workspace_dir
        self.repo: Optional[git.Repo] = None

    def get_authenticated_url(self) -> str:
        token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
        if token and self.repo_url.startswith("https://"):
            clean_url = self.repo_url.replace("https://", "")
            if "@" in clean_url:
                clean_url = clean_url.split("@", 1)[1]
            return f"https://x-access-token:{token.strip()}@{clean_url}"
        return self.repo_url

    def clone_repo(self):
        if os.path.exists(self.workspace_dir):
            shutil.rmtree(self.workspace_dir)
        
        clone_url = self.get_authenticated_url()
        print(f"Cloning {self.repo_url} to {self.workspace_dir}...")
        self.repo = git.Repo.clone_from(clone_url, self.workspace_dir)
        
        # Configure Git User details if available
        try:
            author_name = os.getenv("GIT_AUTHOR_NAME", "Autonomous DevOps Agent")
            author_email = os.getenv("GIT_AUTHOR_EMAIL", "devops-agent@users.noreply.github.com")
            with self.repo.config_writer() as config:
                config.set_value("user", "name", author_name)
                config.set_value("user", "email", author_email)
        except Exception as e:
            logger.warning(f"Could not set git committer identity: {e}")

        current_branch = None
        try:
            current_branch = self.repo.active_branch.name
        except Exception:
            pass

        if current_branch != self.branch_name:
            print(f"Checking out branch {self.branch_name}...")
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
        
        # Update origin remote to use GITHUB_TOKEN if configured
        auth_url = self.get_authenticated_url()
        try:
            self.repo.remote(name="origin").set_url(auth_url)
        except Exception as e:
            logger.warning(f"Could not update remote URL with token: {e}")

        print(f"Pushing changes to {self.branch_name}...")
        
        # Retry logic for push
        max_retries = 3
        import time
        for i in range(max_retries):
            try:
                self.repo.git.push("--force", "--set-upstream", "origin", self.branch_name)
                print("Push successful.")
                return
            except git.GitCommandError as e:
                print(f"Push failed (attempt {i+1}/{max_retries}): {e}")
                if i < max_retries - 1:
                    time.sleep(5) # Wait 5 seconds before retry
                else:
                    raise e
