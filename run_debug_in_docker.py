from backend.agent.sandbox import Sandbox
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    repo_path = "/Users/apple/devops_agent/temp_repo"
    sandbox = Sandbox(repo_path)
    
    # Build image (this might trigger rebuild with trusted-host)
    sandbox.build_image()
    
    # Run debug script
    logger.info("Running debug_models.py in sandbox...")
    # Need to install google-generativeai in the container first?
    # The Dockerfile logs showed pip install ... requests ...
    # It does NOT install google-generativeai by default.
    # I need to install it.
    
    cmd = '/bin/sh -c "pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org google-generativeai && python debug_models.py"'
    
    # Need API Key env var
    # Sandbox implementation passes all env vars?
    # No, it passes specific ones or none?
    # Sandbox.run_command:
    # container = self.client.containers.run(..., environment=self.env_vars, ...)
    # Sandbox.__init__ doesn't set env_vars from host.
    # I need to check Sandbox code.
    
    # Let's check Sandbox code first.
    # But I can pass env vars if I modify Sandbox or just rely on default?
    # Sandbox.run_command doesn't accept env vars.
    # I need to modify it or hardcode it in the command.
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    cmd = f'/bin/sh -c "export GOOGLE_API_KEY={api_key} && pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org google-generativeai && python debug_models.py"'
    
    result = sandbox.run_command(cmd)
    print(result["output"])
    print(f"Exit code: {result['exit_code']}")

if __name__ == "__main__":
    main()
