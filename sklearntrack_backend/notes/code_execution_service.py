# FILE: notes/code_execution_service.py
# ============================================================================

import subprocess
import tempfile
import os
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class CodeExecutionService:
    """Execute code snippets in a sandboxed environment"""
    
    @staticmethod
    def execute_code(code, language):
        """
        Execute code and return output
        Supported languages: python, javascript, java, cpp, c
        """
        try:
            if language == 'python':
                return CodeExecutionService._execute_python(code)
            elif language == 'javascript':
                return CodeExecutionService._execute_javascript(code)
            elif language == 'java':
                return CodeExecutionService._execute_java(code)
            elif language == 'cpp':
                return CodeExecutionService._execute_cpp(code)
            elif language == 'c':
                return CodeExecutionService._execute_c(code)
            else:
                return {
                    'success': False,
                    'output': f"Language '{language}' not supported for execution",
                    'error': True
                }
        except Exception as e:
            logger.error(f"Code execution error: {e}")
            return {
                'success': False,
                'output': f"Execution failed: {str(e)}",
                'error': True
            }
    
    @staticmethod
    def _execute_python(code, input_data=None):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Create input file if needed
            input_args = {}
            if input_data:
                input_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
                input_file.write(input_data)
                input_file.close()
                input_args['stdin'] = open(input_file.name, 'r')
            
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tempfile.gettempdir(),
                **input_args
            )
            output = result.stdout
            error = result.stderr
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'output': f"Error:\n{error}",
                    'error': True
                }
            
            return {
                'success': True,
                'output': output,
                'error': False
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': "Execution timed out (10 seconds)",
                'error': True
            }
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @staticmethod
    def _execute_javascript(code):
        """Execute JavaScript code using Node.js"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(code)
            temp_file = f.name
        
        try:
            result = subprocess.run(
                ['node', temp_file],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tempfile.gettempdir()
            )
            
            output = result.stdout
            error = result.stderr
            
            if result.returncode != 0:
                return {
                    'success': False,
                    'output': f"Error:\n{error}",
                    'error': True
                }
            
            return {
                'success': True,
                'output': output,
                'error': False
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': "Execution timed out (10 seconds)",
                'error': True
            }
        finally:
            if os.path.exists(temp_file):
                os.unlink(temp_file)
    
    @staticmethod
    def _execute_java(code):
        """Execute Java code"""
        # Extract class name from code
        import re
        class_match = re.search(r'class\s+(\w+)', code)
        if not class_match:
            return {
                'success': False,
                'output': "No class found in Java code",
                'error': True
            }
        
        class_name = class_match.group(1)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.java', delete=False) as f:
            f.write(code)
            java_file = f.name
        
        try:
            # Compile Java code
            compile_result = subprocess.run(
                ['javac', java_file],
                capture_output=True,
                text=True,
                cwd=tempfile.gettempdir()
            )
            
            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'output': f"Compilation error:\n{compile_result.stderr}",
                    'error': True
                }
            
            # Execute compiled class
            exec_result = subprocess.run(
                ['java', '-cp', tempfile.gettempdir(), class_name],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            output = exec_result.stdout
            error = exec_result.stderr
            
            if exec_result.returncode != 0:
                return {
                    'success': False,
                    'output': f"Execution error:\n{error}",
                    'error': True
                }
            
            return {
                'success': True,
                'output': output,
                'error': False
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': "Execution timed out (10 seconds)",
                'error': True
            }
        finally:
            # Cleanup files
            if os.path.exists(java_file):
                os.unlink(java_file)
            class_file = os.path.join(tempfile.gettempdir(), f"{class_name}.class")
            if os.path.exists(class_file):
                os.unlink(class_file)
    @staticmethod
    def _execute_cpp(code):
        """Execute C++ code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.cpp', delete=False) as f:
            f.write(code)
            cpp_file = f.name
        
        try:
            # Compile C++ code
            executable = os.path.join(tempfile.gettempdir(), 'program')
            compile_result = subprocess.run(
                ['g++', cpp_file, '-o', executable, '-std=c++11'],
                capture_output=True,
                text=True,
                cwd=tempfile.gettempdir()
            )
            
            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'output': f"Compilation error:\n{compile_result.stderr}",
                    'error': True
                }
            
            # Execute compiled program
            exec_result = subprocess.run(
                [executable],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tempfile.gettempdir()
            )
            
            output = exec_result.stdout
            error = exec_result.stderr
            
            if exec_result.returncode != 0:
                return {
                    'success': False,
                    'output': f"Execution error:\n{error}",
                    'error': True
                }
            
            return {
                'success': True,
                'output': output,
                'error': False
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': "Execution timed out (10 seconds)",
                'error': True
            }
        finally:
            # Cleanup files
            if os.path.exists(cpp_file):
                os.unlink(cpp_file)
            if os.path.exists(executable):
                os.unlink(executable)
    
    @staticmethod
    def _execute_c(code):
        """Execute C code"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.c', delete=False) as f:
            f.write(code)
            c_file = f.name
        
        try:
            # Compile C code
            executable = os.path.join(tempfile.gettempdir(), 'program')
            compile_result = subprocess.run(
                ['gcc', c_file, '-o', executable],
                capture_output=True,
                text=True,
                cwd=tempfile.gettempdir()
            )
            
            if compile_result.returncode != 0:
                return {
                    'success': False,
                    'output': f"Compilation error:\n{compile_result.stderr}",
                    'error': True
                }
            
            # Execute compiled program
            exec_result = subprocess.run(
                [executable],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=tempfile.gettempdir()
            )
            
            output = exec_result.stdout
            error = exec_result.stderr
            
            if exec_result.returncode != 0:
                return {
                    'success': False,
                    'output': f"Execution error:\n{error}",
                    'error': True
                }
            
            return {
                'success': True,
                'output': output,
                'error': False
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'output': "Execution timed out (10 seconds)",
                'error': True
            }
        finally:
            # Cleanup files
            if os.path.exists(c_file):
                os.unlink(c_file)
            if os.path.exists(executable):
                os.unlink(executable)