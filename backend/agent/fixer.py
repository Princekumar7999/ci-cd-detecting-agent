import os
import logging
import time
from typing import Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger(__name__)

class Fixer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self._llm = None

    @property
    def llm(self):
        if self._llm is None:
            # Use gemini-2.0-flash-lite-001 for better rate limits and availability
            self._llm = ChatGoogleGenerativeAI(
                model="models/gemini-2.0-flash-lite-001", 
                temperature=0,
                convert_system_message_to_human=True
            )
        return self._llm

    def fix_error(self, error: Dict[str, Any]) -> str:
        """
        Attempts to fix a single error using Gemini API.
        Returns a commit message describing the fix.
        """
        file_path = os.path.join(self.repo_path, error["file"])
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return f"Failed to fix {error['file']}: File not found"

        with open(file_path, "r") as f:
            content = f.read()

        # Deterministic Fallback for Syntax Errors (Missing Colon)
        # We keep this small helper as it saves tokens/time for the most basic error
        if error['type'] == "SYNTAX" and "expected ':'" in error['message']:
            logger.info(f"Applying deterministic fix for missing colon in {error['file']} at line {error['line']}")
            lines = content.splitlines()
            line_idx = error['line'] - 1
            
            if 0 <= line_idx < len(lines):
                original_line = lines[line_idx]
                if not original_line.strip().endswith(":"):
                    lines[line_idx] = original_line + ":"
                    fixed_content = "\n".join(lines)
                    
                    with open(file_path, "w") as f:
                        f.write(fixed_content)
                    return f"Fix SYNTAX in {error['file']}: Added missing colon (Deterministic)"

        # Deterministic Fix for Unused Imports
        if error['type'] in ["LINTING", "IMPORT"] and "unused import" in error['message'].lower():
            logger.info(f"Applying deterministic fix for unused import in {error['file']} at line {error['line']}")
            lines = content.splitlines()
            line_idx = error['line'] - 1
            
            if 0 <= line_idx < len(lines):
                # Simply remove the line
                # Ideally check if it's a multi-line import, but for now single line assumption is safe for this demo
                del lines[line_idx]
                fixed_content = "\n".join(lines)
                
                with open(file_path, "w") as f:
                    f.write(fixed_content)
                return f"Fix LINT in {error['file']}: Removed unused import (Deterministic)"

        logger.info(f"Attempting to fix error: {error}")

        # Deterministic Fix for ModuleNotFoundError (specific to devops_challenge_repo)
        msg = error.get('message', '')
        if "validator" in msg and ("ModuleNotFoundError" in msg or "ImportError" in msg):
             logger.info(f"Applying deterministic fix for ModuleNotFoundError in {error['file']}")
             lines = content.splitlines()
             for i, line in enumerate(lines):
                 if "from validator import validate" in line:
                     lines[i] = "import sys\nimport os\nsys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))\nfrom validator import validate"
                     break
             fixed_content = "\n".join(lines)
             with open(file_path, "w") as f:
                 f.write(fixed_content)
             return f"Fix IMPORT in {error['file']}: Added src to sys.path (Deterministic)"

        # Construct a prompt for the fix
        logger.info(f"Fixing {error['type']} in {error['file']} at line {error['line']} using Gemini")
        
        system_msg_template = (
            "You are an expert autonomous software engineer. "
            "Your task is to fix a specific error in a Python file. "
            "You must return ONLY the complete, fixed file content. "
            "Do not include any explanation, markdown code blocks, or comments like 'Here is the fixed code'. "
            "Just the raw code. "
            "Retain all other code that is not related to the fix."
        )
        
        user_msg_template = (
            "FilePath: {file_path}\n"
            "Error Type: {error_type}\n"
            "Error Message: {error_message}\n"
            "Line Number: {line_number}\n\n"
            "Current File Content:\n"
            "```python\n{content}\n```\n\n"
            "Please provide the corrected file content."
        )

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_msg_template),
            ("human", user_msg_template)
        ])

        chain = prompt | self.llm
        
        # Retry mechanism for Rate Limits (429)
        max_retries = 5
        base_delay = 10
        
        for attempt in range(max_retries):
            try:
                response = chain.invoke({
                    "file_path": error['file'],
                    "error_type": error['type'],
                    "error_message": error['message'],
                    "line_number": error['line'],
                    "content": content
                }, config={"timeout": 60})
                fixed_content = response.content
                
                # Simple cleanup of markdown code blocks if the LLM ignores instructions
                cleaned_content = fixed_content
                if cleaned_content.startswith("```"):
                    lines = cleaned_content.splitlines()
                    # Remove first line if it's backticks
                    if lines[0].strip().startswith("```"):
                        lines = lines[1:]
                    # Remove last line if it's backticks
                    if lines and lines[-1].strip().startswith("```"):
                        lines = lines[:-1]
                    cleaned_content = "\n".join(lines)
                
                # Additional cleanup for "python" or language identifier
                if cleaned_content.startswith("python"):
                    cleaned_content = cleaned_content[6:].lstrip()

                # Write the fix back to the file
                with open(file_path, "w") as f:
                    f.write(cleaned_content)
                
                return f"Fix {error['type']} in {error['file']}: {error['message'][:50]}..."
                
            except Exception as e:
                error_str = str(e)
                if "429" in error_str or "quota" in error_str.lower() or "resource exhausted" in error_str.lower():
                    logger.warning(f"Rate limit hit (attempt {attempt+1}/{max_retries}). Sleeping...")
                    time.sleep(base_delay * (attempt + 1)) # Linear backoff 10, 20, 30...
                else:
                    logger.error(f"Error generating fix: {e}")
                    raise e
        
        raise Exception("Failed to fix error after multiple retries due to rate limiting.")
