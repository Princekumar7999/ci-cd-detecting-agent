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

        try:
            self.client.images.build(path=self.repo_path, tag=self.image_tag, rm=True)
            logger.info(f"Image {self.image_tag} built successfully.")
        except docker.errors.BuildError as e:
            logger.error(f"Error building image: {e}")
            raise
        finally:
            # Cleanup generated Dockerfile
            if created_dockerfile and os.path.exists(dockerfile_path):
                os.remove(dockerfile_path)

    def run_command(self, command: str) -> dict:
        """Runs a command in the sandbox container."""
        logger.info(f"Running command in sandbox: {command}")
        try:
            container = self.client.containers.run(
                self.image_tag,
                command,
                detach=True,
                remove=False  # We want to inspect exit code
            )
            exit_code = container.wait()['StatusCode']
            logs = container.logs().decode("utf-8")
            container.remove()
            
            return {
                "exit_code": exit_code,
                "output": logs
            }
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
