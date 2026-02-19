import docker
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Sandbox:
    def __init__(self, repo_path: str):
        self.client = docker.from_env()
        self.repo_path = repo_path
        self.image_tag = "agent-sandbox:latest"

    def build_image(self):
        """Builds a Docker image for the repository."""
        logger.info(f"Building Docker image for {self.repo_path}")
        
        # Check if Dockerfile exists, if not create a default one
        dockerfile_path = os.path.join(self.repo_path, "Dockerfile")
        created_dockerfile = False
        
        if not os.path.exists(dockerfile_path):
            logger.info("No Dockerfile found. Creating default python:3.11-slim Dockerfile.")
            with open(dockerfile_path, "w") as f:
                f.write("""
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN if [ -f requirements.txt ]; then pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt; fi
# Install test runners
RUN pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org pytest pylint
""")
            created_dockerfile = True

        # Try to remove existing image first to avoid conflicts
        try:
            self.client.images.remove(self.image_tag, force=True)
        except Exception:
            pass

        # Retry mechanism for build
        import time
        max_retries = 1
        for attempt in range(max_retries):
            try:
                self.client.images.build(path=self.repo_path, tag=self.image_tag, rm=True)
                logger.info(f"Image {self.image_tag} built successfully.")
                break
            except docker.errors.BuildError as e:
                logger.warning(f"Build failed (attempt {attempt+1}): {e}")
                if attempt == max_retries - 1:
                    logger.error("Final build attempt failed.")
                    raise
                time.sleep(2)
            except Exception as e:
                logger.error(f"Unexpected build error: {e}")
                raise
        
        # Cleanup generated Dockerfile
        if created_dockerfile and os.path.exists(dockerfile_path):
            os.remove(dockerfile_path)

    def run_command(self, command: str, timeout: int = 60) -> dict:
        """Runs a command in the sandbox container with a timeout."""
        logger.info(f"Running command in sandbox: {command} (timeout={timeout}s)")
        try:
            container = self.client.containers.run(
                self.image_tag,
                command,
                detach=True,
                # remove=False is critical to inspect exit code
            )
            
            # Poll for completion
            import time
            start_time = time.time()
            
            while True:
                # Check status
                container.reload()
                if container.status == 'exited':
                    result = container.wait()
                    exit_code = result['StatusCode']
                    logs = container.logs().decode("utf-8")
                    container.remove()
                    return {
                        "exit_code": exit_code,
                        "output": logs
                    }
                
                # Check timeout
                if time.time() - start_time > timeout:
                    logger.error(f"Command timed out after {timeout}s: {command}")
                    try:
                        container.kill()
                        logs = container.logs().decode("utf-8") # Try to get partial logs
                    except Exception:
                        logs = "Timeout (logs unavailable)"
                    
                    try:
                        container.remove()
                    except Exception:
                        pass
                        
                    return {
                        "exit_code": -1, # Custom code for timeout
                        "output": f"TIMEOUT ERROR: execution exceeded {timeout} seconds.\nPartial Logs:\n{logs}",
                        "timeout": True
                    }
                
                time.sleep(1) # Poll interval
                
        except docker.errors.ContainerError as e:
            return {
                "exit_code": e.exit_status,
                "output": e.stderr.decode("utf-8") if e.stderr else e.stdout.decode("utf-8")
            }
        except Exception as e:
            logger.error(f"Error running command: {e}")
            return {
                "exit_code": -1,
                "output": str(e)
            }
