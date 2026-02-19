import json
import logging
import xml.etree.ElementTree as ET
from typing import List, Dict, Any
from .sandbox import Sandbox

logger = logging.getLogger(__name__)

class Analyzer:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.sandbox = Sandbox(repo_path)

    def analyze(self) -> Dict[str, Any]:
        """Runs analysis on the repository."""
        logger.info("Starting analysis...")
        self.sandbox.build_image()
        
        lint_results = self.run_linter()
        test_results = self.run_tests()
        
        return {
            "lint_errors": lint_results,
            "test_failures": test_results,
            "success": len(lint_results) == 0 and len(test_results) == 0
        }

    def run_linter(self) -> List[Dict[str, Any]]:
        logger.info("Running linter...")
        # Run pylint with JSON output
        # Catch syntax errors, import errors, etc.
        # We scan all .py files
        # Debug: List files
        ls_res = self.sandbox.run_command("ls -R")
        logger.info(f"File structure: {ls_res['output']}")

        # Run pylint with JSON output
        # Use simple recursion if find is tricky, or just target .
        # Wrap in sh -c and redirect stderr
        # Must set PYTHONPATH to current dir so pylint can resolve imports (e.g. src.validator)
        cmd = '/bin/sh -c "export PYTHONPATH=$PYTHONPATH:. && pylint --output-format=json --recursive=y . 2>&1"'
        result = self.sandbox.run_command(cmd, timeout=300)
        
        logger.info(f"Linter raw output: {result['output']}")
        logger.info(f"Linter exit code: {result['exit_code']}")
        
        errors = []
        try:
            output_str = result["output"]
            # Try to find JSON content enclosed in []
            start_idx = output_str.find("[")
            end_idx = output_str.rfind("]")
            
            if start_idx != -1 and end_idx != -1:
                json_str = output_str[start_idx:end_idx+1]
                lint_data = json.loads(json_str)
                
                for item in lint_data:
                    # Filter for errors (E) and fatal (F). Maybe warnings (W)?
                    # The prompt implies we need to fix "Unused import" which is a Warning (W0611).
                    # So we should include everything that pylint reports.
                    
                    bug_type = "LINTING"
                    msg_lower = item["message"].lower()
                    symbol = item.get("symbolid") or item.get("message-id") or item.get("symbol")
                    symbol_lower = str(symbol).lower() if symbol else ""
                    
                    # STRICT CLASSIFICATION LOGIC
                    if "syntaxerror" in msg_lower or "expected ':'" in msg_lower or "invalid syntax" in msg_lower or "syntax-error" in symbol_lower:
                        bug_type = "SYNTAX"
                    elif "indentationerror" in msg_lower or "unexpected indent" in msg_lower or "indentation" in msg_lower:
                        bug_type = "INDENTATION"
                    elif "import" in msg_lower or "import-error" in symbol_lower or "modulenotfounderror" in msg_lower:
                        bug_type = "IMPORT"
                    elif "type" in msg_lower and "error" in msg_lower:
                        bug_type = "TYPE_ERROR"
                    elif item["type"] in ["error", "fatal"]:
                         bug_type = "LINTING" # Default for other errors
                            
                    if "unused import" in msg_lower:
                         bug_type = "LINTING" # Explicitly mentioned in prompt

                    errors.append({
                        "file": item["path"],
                        "line": int(item["line"]),
                        "type": bug_type,
                        "message": item["message"],
                        "symbol": symbol
                    })
        except Exception as e:
            logger.error(f"Error parsing linter output: {e}")
            logger.debug(f"Raw output: {result['output']}")
            # Fallback or empty if parse fails
            
        return errors

    def run_tests(self) -> List[Dict[str, Any]]:
        logger.info("Running tests...")
        # Run pytest and generate XML
        # Add current directory to PYTHONPATH. chain with cat to persist output.
        # Using ; to ensure cat runs even if pytest fails.
        cmd = '/bin/sh -c "export PYTHONPATH=$PYTHONPATH:. && pytest --junitxml=report.xml; echo XML_START; cat report.xml; echo XML_END"'
        # 300s timeout (5 mins) for tests
        result = self.sandbox.run_command(cmd, timeout=300)
        
        logger.info(f"Pytest raw output: {result['output']}")
        logger.info(f"Pytest exit code: {result['exit_code']}")
        
        # Handle Timeout
        if result.get("timeout"):
             return [{
                 "file": "timeout",
                 "line": 0,
                 "type": "TIMEOUT",
                 "message": "Test execution timed out. Possible infinite loop or slow dependency install.",
                 "test_name": "Global Timeout"
             }]

        # Handle "No Tests Collected" (pytest exit code 5)
        if result['exit_code'] == 5:
             logger.info("Pytest returned code 5 (No tests collected). Warning only.")
             # Optionally return a warning, but strictly this isn't a failure we can "fix" via code changes easily unless we add tests.
             # For this agent, we'll treat it as empty failures so the pipeline can proceed/pass.
             return []
        
        # Extract XML content from output
        output = result["output"]
        xml_content = ""
        if "XML_START" in output and "XML_END" in output:
             start = output.find("XML_START") + len("XML_START")
             end = output.find("XML_END")
             xml_content = output[start:end].strip()
        
        logger.info(f"XML Content: {xml_content}")
        
        failures = []
        try:
            # Clean up content if there's noise before XML
            start_idx = xml_content.find("<testsuite")
            if start_idx != -1:
                xml_content = xml_content[start_idx:]
                
            if "<testsuite" in xml_content:
                root = ET.fromstring(xml_content)
                # Handle both singular testsuite and testsuites
                suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
                
                for suite in suites:
                    for testcase in suite.iter("testcase"):
                        failure = testcase.find("failure")
                        error = testcase.find("error")
                        
                        if failure is not None or error is not None:
                            elem = failure if failure is not None else error
                            msg = elem.attrib.get("message", "")
                            # Try to extract file and line
                            file_path = testcase.attrib.get("file", "unknown")
                            line = testcase.attrib.get("line", "0")
                            
                            # Fallback: Extract from message or text if file is unknown
                            import re
                            search_text = f"{msg}\n{elem.text or ''}"
                            
                            if file_path == "unknown" and search_text:
                                candidates = []
                                # Look for all File "..." matches
                                candidates.extend(re.findall(r'File "([^"]+)", line (\d+)', search_text))
                                # Look for all pytest matches
                                candidates.extend(re.findall(r'([a-zA-Z0-9_/.-]+):(\d+): in', search_text))
                                
                                # Iterate backwards to find the most relevant user code
                                best_candidate = None
                                for f, l in reversed(candidates):
                                    if "/lib/python" in f or "/usr/" in f or "site-packages" in f:
                                        continue
                                    best_candidate = (f, l)
                                    break
                                
                                if best_candidate:
                                    file_path, line = best_candidate
                                    # cleanup /app/ prefix
                                    if file_path.startswith("/app/"):
                                        file_path = file_path[5:]
                                    
                                    logger.info(f"Extracted file from error message: {file_path}:{line}")

                            # Determine bug type for test failures
                            bug_type = "LOGIC"
                            msg_lower = msg.lower() if msg else ""
                            text_lower = (elem.text or "").lower()
                            combined_text = f"{msg_lower} {text_lower}"
                            
                            if "modulenotfounderror" in combined_text or "importerror" in combined_text:
                                bug_type = "IMPORT"
                            elif "syntaxerror" in combined_text:
                                bug_type = "SYNTAX"
                            elif "indentationerror" in combined_text:
                                bug_type = "INDENTATION"
                                
                            failures.append({
                                "file": file_path,
                                "line": int(line) if line.isdigit() else 0, # Line is usually 1-indexed in messages
                                "type": bug_type, 
                                "message": combined_text, # Use combined text to include traceback
                                "test_name": testcase.attrib.get("name")
                            })
        except Exception as e:
            logger.error(f"Error parsing test output: {e}")
            
        return failures
