# notes/code_execution_service.py
# Advanced, fast, stdin-enabled code runner using Piston API

import time
import requests
from typing import Dict, Any
import json

PISTON_URL = "https://emkc.org/api/v2/piston/execute"
DEFAULT_TIMEOUT = 12

LANGUAGE_MAP = {
    "python": {"lang": "python", "version": "3.10.0", "ext": "py"},
    "javascript": {"lang": "javascript", "version": "18.15.0", "ext": "js"},
    "typescript": {"lang": "typescript", "version": "5.0.3", "ext": "ts"},
    "java": {"lang": "java", "version": "15.0.2", "ext": "java"},
    "c": {"lang": "c", "version": "10.2.0", "ext": "c"},
    "cpp": {"lang": "c++", "version": "10.2.0", "ext": "cpp"},
    "go": {"lang": "go", "version": "1.16.2", "ext": "go"},
    "rust": {"lang": "rust", "version": "1.68.2", "ext": "rs"},
    "bash": {"lang": "bash", "version": "5.2.0", "ext": "sh"},
    "sql": {"lang": "sqlite3", "version": "3.36.0", "ext": "sql"},
}

class CodeExecutionService:
    @staticmethod
    def execute_code(code: str, language: str = "python", stdin: str = "",
                     timeout: int = DEFAULT_TIMEOUT, memory_limit: int = 128) -> Dict[str, Any]:
        language = language.lower()
        if language not in LANGUAGE_MAP:
            return {"success": False, "output": "", "error": f"Unsupported language: {language}",
                    "exit_code": None, "runtime_ms": 0}

        cfg = LANGUAGE_MAP[language]
        payload = {
            "language": cfg["lang"],
            "version": cfg["version"],
            "files": [{"name": f"main.{cfg['ext']}", "content": code}],
            "stdin": stdin,
            "run_timeout": timeout * 1000,  # Piston expects milliseconds
            "compile_timeout": timeout * 1000,
        }

        start = time.perf_counter()
        try:
            # Add headers and increase timeout
            r = requests.post(
                PISTON_URL, 
                json=payload, 
                timeout=(timeout + 10),
                headers={'Content-Type': 'application/json'}
            )
            runtime_ms = round((time.perf_counter() - start) * 1000, 2)

            if r.status_code != 200:
                error_msg = f"API Error ({r.status_code}): "
                try:
                    error_msg += r.json().get('message', r.text)
                except:
                    error_msg += r.text[:200]
                return {"success": False, "output": "", "error": error_msg,
                        "exit_code": None, "runtime_ms": runtime_ms}

            data = r.json()
            
            # Check for runtime error first
            if 'run' not in data:
                return {"success": False, "output": "", "error": "No execution output received",
                        "exit_code": 1, "runtime_ms": runtime_ms}
            
            run = data.get("run", {})
            compile_res = data.get("compile", {})

            # Check compilation errors
            if compile_res and compile_res.get("code", 0) != 0:
                error_output = compile_res.get("stderr", "") or compile_res.get("stdout", "")
                return {"success": False, "output": compile_res.get("stdout", ""),
                        "error": error_output,
                        "exit_code": compile_res.get("code"),
                        "runtime_ms": runtime_ms}

            # Check runtime errors
            exit_code = run.get("code", 1)
            output = run.get("stdout", "")
            error = run.get("stderr", "")
            
            # If stderr is empty but exit code is non-zero, check output for errors
            if not error and exit_code != 0 and output:
                # Sometimes errors are in stdout
                if "error" in output.lower() or "exception" in output.lower() or "traceback" in output.lower():
                    error = output
                    output = ""
            
            # Special handling for Python input()
            if language == "python" and "input" in code.lower() and not stdin:
                # Check if code expects input
                lines = code.split('\n')
                has_input = any('input(' in line.lower() for line in lines)
                if has_input:
                    return {
                        "success": False, 
                        "output": "", 
                        "error": "This code requires input. Please provide input in the stdin field.",
                        "exit_code": None,
                        "runtime_ms": runtime_ms,
                        "requires_input": True
                    }

            return {
                "success": exit_code == 0,
                "output": output,
                "error": error,
                "exit_code": exit_code,
                "runtime_ms": runtime_ms
            }

        except requests.exceptions.Timeout:
            return {"success": False, "output": "", "error": "Execution timeout. The code took too long to run.",
                    "exit_code": None, "runtime_ms": 0}
        except requests.exceptions.ConnectionError:
            return {"success": False, "output": "", "error": "Connection error. Please check your internet connection.",
                    "exit_code": None, "runtime_ms": 0}
        except Exception as e:
            error_msg = str(e)
            if "Max retries exceeded" in error_msg:
                return {"success": False, "output": "", "error": "Service unavailable. Please try again later.",
                        "exit_code": None, "runtime_ms": 0}
            return {"success": False, "output": "", "error": f"Execution failed: {error_msg}",
                    "exit_code": None, "runtime_ms": 0}