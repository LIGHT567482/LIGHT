"""
LIGHT - Comprehensive Coder & Programmer Assistant
Unified module for code generation, completion, file generation, and IDE integration

Combines:
- CodeCompletion: Copilot-like code suggestions and completions
- FileGenerator: Generate individual files, classes, modules, tests
- IDEIntegration: Export projects for any IDE (VS Code, PyCharm, etc.)

Usage:
    from light_coder_assistant import CodeCompletion, FileGenerator, IDEIntegration
    
    # Code completion
    completer = CodeCompletion()
    completions = completer.complete_function("def my_function(param):", "python")
    
    # File generation
    gen = FileGenerator()
    result = gen.generate_class("User", ["name", "email"], ["login", "logout"])
    
    # IDE export
    exporter = IDEIntegration()
    vs_code_export = exporter.export_for_vscode("my_project", {"main.py": code})
"""

import os
import json
import re
import zipfile
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from contextlib import contextmanager


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 1: CODE COMPLETION (Copilot-like Suggestions)
# ═══════════════════════════════════════════════════════════════════════════════

class CodeCompletion:
    """
    Provides Copilot-like code completion, suggestions, and improvements
    """
    
    def __init__(self, context_dir: Optional[str] = None):
        self.context_dir = context_dir or os.getcwd()
        self.suggestions_history = []
        self.load_context_files()
    
    def load_context_files(self):
        """Load context from existing code files in the project"""
        self.context_files = []
        for root, dirs, files in os.walk(self.context_dir):
            for file in files:
                if file.endswith(('.py', '.js', '.ts', '.java', '.cpp', '.c', '.html', '.css')):
                    self.context_files.append(os.path.join(root, file))
    
    def complete_function(self, function_signature: str, language: str = "python") -> Dict:
        """
        Auto-complete a function based on its signature (Copilot-like)
        
        Args:
            function_signature: The function declaration/signature
            language: Programming language (python, javascript, etc.)
        
        Returns:
            Dictionary with completion suggestions
        """
        completions = []
        
        if language.lower() in ["python", "py"]:
            completions = self._complete_python_function(function_signature)
        elif language.lower() in ["javascript", "js"]:
            completions = self._complete_js_function(function_signature)
        elif language.lower() in ["typescript", "ts"]:
            completions = self._complete_ts_function(function_signature)
        elif language.lower() in ["java"]:
            completions = self._complete_java_function(function_signature)
        
        result = {
            "success": True,
            "original_signature": function_signature,
            "language": language,
            "completions": completions,
            "timestamp": datetime.now().isoformat()
        }
        
        self.suggestions_history.append(result)
        return result
    
    def _complete_python_function(self, signature: str) -> List[Dict]:
        """Generate Python function completions"""
        completions = []
        
        # Extract function name and parameters
        match = re.search(r'def\s+(\w+)\s*\((.*?)\)', signature)
        if not match:
            return completions
        
        func_name = match.group(1)
        params = match.group(2)
        
        # Suggestion 1: Basic implementation
        basic_impl = f"""def {func_name}({params}):
    \"\"\"Function implementation for {func_name}\"\"\"
    pass
"""
        completions.append({
            "type": "basic",
            "code": basic_impl,
            "description": "Basic function skeleton with docstring"
        })
        
        # Suggestion 2: With error handling
        error_handling = f"""def {func_name}({params}):
    \"\"\"Function implementation for {func_name}\"\"\"
    try:
        # Your implementation here
        pass
    except Exception as e:
        print(f"Error in {func_name}: {{e}}")
        raise
"""
        completions.append({
            "type": "with_error_handling",
            "code": error_handling,
            "description": "Function with try-except error handling"
        })
        
        # Suggestion 3: With logging
        with_logging = f"""import logging

logger = logging.getLogger(__name__)

def {func_name}({params}):
    \"\"\"Function implementation for {func_name}\"\"\"
    logger.info(f"Calling {func_name} with params: {{locals()}}")
    try:
        result = None  # Implement logic here
        logger.info(f"{func_name} completed successfully")
        return result
    except Exception as e:
        logger.error(f"Error in {func_name}: {{e}}", exc_info=True)
        raise
"""
        completions.append({
            "type": "with_logging",
            "code": with_logging,
            "description": "Function with logging and error handling"
        })
        
        # Suggestion 4: Async variant (if async keyword in params)
        if "async" in signature.lower():
            async_impl = f"""async def {func_name}({params}):
    \"\"\"Async function implementation for {func_name}\"\"\"
    try:
        # Your async implementation here
        result = await some_async_operation()
        return result
    except Exception as e:
        print(f"Error in {func_name}: {{e}}")
        raise
"""
            completions.append({
                "type": "async",
                "code": async_impl,
                "description": "Async function implementation"
            })
        
        return completions
    
    def _complete_js_function(self, signature: str) -> List[Dict]:
        """Generate JavaScript function completions"""
        completions = []
        
        match = re.search(r'(?:function\s+)?(\w+)\s*\((.*?)\)', signature)
        if not match:
            return completions
        
        func_name = match.group(1)
        params = match.group(2)
        
        # Basic implementation
        basic = f"""function {func_name}({params}) {{
    // Implementation
    return null;
}}"""
        completions.append({
            "type": "basic",
            "code": basic,
            "description": "Basic function implementation"
        })
        
        # With error handling
        error_handling = f"""function {func_name}({params}) {{
    try {{
        // Your implementation here
        return null;
    }} catch (error) {{
        console.error('Error in {func_name}:', error);
        throw error;
    }}
}}"""
        completions.append({
            "type": "with_error_handling",
            "code": error_handling,
            "description": "Function with try-catch error handling"
        })
        
        # Arrow function variant
        arrow = f"""const {func_name} = ({params}) => {{
    try {{
        // Implementation
        return null;
    }} catch (error) {{
        console.error('Error:', error);
        throw error;
    }}
}};"""
        completions.append({
            "type": "arrow_function",
            "code": arrow,
            "description": "Arrow function with error handling"
        })
        
        # Async variant
        if "await" in signature.lower() or "async" in signature.lower():
            async_impl = f"""async function {func_name}({params}) {{
    try {{
        // Your async implementation
        const result = await someAsyncOperation();
        return result;
    }} catch (error) {{
        console.error('Error in {func_name}:', error);
        throw error;
    }}
}}"""
            completions.append({
                "type": "async",
                "code": async_impl,
                "description": "Async function implementation"
            })
        
        return completions
    
    def _complete_ts_function(self, signature: str) -> List[Dict]:
        """Generate TypeScript function completions"""
        completions = []
        
        # Extract function name
        match = re.search(r'(?:function\s+)?(\w+)\s*\((.*?)\)', signature)
        if not match:
            return completions
        
        func_name = match.group(1)
        params = match.group(2)
        
        # With type annotations
        typed = f"""function {func_name}({params}): any {{
    try {{
        // Your implementation
        return null;
    }} catch (error) {{
        console.error('Error:', error);
        throw error;
    }}
}}"""
        completions.append({
            "type": "typed",
            "code": typed,
            "description": "TypeScript function with type hints"
        })
        
        # Handler/Middleware style
        handler = f"""export async function {func_name}({params}): Promise<any> {{
    try {{
        // Your implementation
        return {{"success": true, "data": null}};
    }} catch (error) {{
        console.error('Error:', error);
        return {{"success": false, "error": error.message}};
    }}
}}"""
        completions.append({
            "type": "handler",
            "code": handler,
            "description": "TypeScript handler/API endpoint"
        })
        
        return completions
    
    def _complete_java_function(self, signature: str) -> List[Dict]:
        """Generate Java function completions"""
        completions = []
        
        match = re.search(r'(\w+)\s+(\w+)\s*\((.*?)\)', signature)
        if not match:
            return completions
        
        return_type = match.group(1)
        func_name = match.group(2)
        params = match.group(3)
        
        basic = f"""public {return_type} {func_name}({params}) {{
    // Implementation
    return null;
}}"""
        completions.append({
            "type": "basic",
            "code": basic,
            "description": "Basic Java method"
        })
        
        with_javadoc = f"""/**
 * Implementation of {func_name}
 * @param {params.split(',')[0] if params else 'param'} parameter description
 * @return return value description
 */
public {return_type} {func_name}({params}) {{
    try {{
        // Implementation
        return null;
    }} catch (Exception e) {{
        logger.error("Error in {func_name}", e);
        throw new RuntimeException(e);
    }}
}}"""
        completions.append({
            "type": "with_javadoc",
            "code": with_javadoc,
            "description": "Java method with JavaDoc and error handling"
        })
        
        return completions
    
    def suggest_improvements(self, code: str, language: str = "python") -> Dict:
        """
        Analyze code and suggest improvements (like Copilot)
        
        Args:
            code: The code to analyze
            language: Programming language
        
        Returns:
            Dictionary with improvement suggestions
        """
        suggestions = []
        
        # Analyze code quality
        suggestions.extend(self._check_code_quality(code, language))
        
        # Suggest optimizations
        suggestions.extend(self._suggest_optimizations(code, language))
        
        # Suggest best practices
        suggestions.extend(self._suggest_best_practices(code, language))
        
        result = {
            "success": True,
            "language": language,
            "code_length": len(code.split('\n')),
            "suggestions": suggestions,
            "total_suggestions": len(suggestions),
            "timestamp": datetime.now().isoformat()
        }
        
        self.suggestions_history.append(result)
        return result
    
    def _check_code_quality(self, code: str, language: str) -> List[Dict]:
        """Check code quality issues"""
        suggestions = []
        lines = code.split('\n')
        
        # Check for long lines
        for i, line in enumerate(lines):
            if len(line) > 100:
                suggestions.append({
                    "type": "line_length",
                    "line": i + 1,
                    "severity": "minor",
                    "message": f"Line {i + 1} is {len(line)} characters (>100)",
                    "suggestion": "Consider breaking this line into multiple lines"
                })
        
        # Check for code duplication
        if len(lines) > 1:
            unique_lines = len(set(lines))
            if unique_lines < len(lines) * 0.7:
                suggestions.append({
                    "type": "duplication",
                    "severity": "medium",
                    "message": "Detected potential code duplication",
                    "suggestion": "Consider extracting repeated code into functions"
                })
        
        # Check for missing docstrings (Python)
        if language.lower() in ["python", "py"]:
            if "\"\"\"" not in code and "'''" not in code:
                suggestions.append({
                    "type": "missing_docstring",
                    "severity": "minor",
                    "message": "No docstrings found",
                    "suggestion": "Add docstrings to document functions and classes"
                })
        
        # Check for commented code
        if "#" in code and language.lower() in ["python", "py"]:
            commented = [l for l in lines if l.strip().startswith("#")]
            if len(commented) > len(lines) * 0.2:
                suggestions.append({
                    "type": "excessive_comments",
                    "severity": "minor",
                    "message": f"High ratio of commented code ({len(commented)} lines)",
                    "suggestion": "Clean up commented-out code"
                })
        
        return suggestions
    
    def _suggest_optimizations(self, code: str, language: str) -> List[Dict]:
        """Suggest performance optimizations"""
        suggestions = []
        
        if language.lower() in ["python", "py"]:
            # Check for common Python inefficiencies
            if "for " in code and "in range(len(" in code:
                suggestions.append({
                    "type": "optimization",
                    "severity": "medium",
                    "message": "Detected range(len()) pattern",
                    "suggestion": "Use enumerate() instead of range(len()) for better performance",
                    "example": "for i, item in enumerate(items):"
                })
            
            if ".append(" in code and "for " in code:
                suggestions.append({
                    "type": "optimization",
                    "severity": "medium",
                    "message": "List comprehension might be faster",
                    "suggestion": "Consider using list comprehension instead of append in loops",
                    "example": "[process(item) for item in items]"
                })
        
        elif language.lower() in ["javascript", "js"]:
            if "var " in code:
                suggestions.append({
                    "type": "optimization",
                    "severity": "medium",
                    "message": "Using var instead of const/let",
                    "suggestion": "Use const for variables that don't change, let for those that do",
                    "note": "var has function scope; const and let have block scope"
                })
            
            if "== " in code:
                suggestions.append({
                    "type": "optimization",
                    "severity": "high",
                    "message": "Using loose equality (==) instead of strict (===)",
                    "suggestion": "Use === for type-safe comparisons",
                    "example": "if (x === 'true')"
                })
        
        return suggestions
    
    def _suggest_best_practices(self, code: str, language: str) -> List[Dict]:
        """Suggest best practices"""
        suggestions = []
        
        # General best practices
        if len(code) > 500 and "\n\n" not in code:
            suggestions.append({
                "type": "best_practice",
                "severity": "minor",
                "message": "Code lacks logical separation",
                "suggestion": "Add blank lines between logical sections for readability"
            })
        
        # Language-specific
        if language.lower() in ["python", "py"]:
            if "import *" in code:
                suggestions.append({
                    "type": "best_practice",
                    "severity": "high",
                    "message": "Using wildcard imports",
                    "suggestion": "Import specific items instead of using import *",
                    "reason": "Makes dependencies clear and avoids namespace pollution"
                })
            
            if "except:" in code:
                suggestions.append({
                    "type": "best_practice",
                    "severity": "high",
                    "message": "Bare except clause detected",
                    "suggestion": "Catch specific exceptions instead of bare except",
                    "example": "except ValueError as e:"
                })
        
        return suggestions
    
    def generate_from_docstring(self, docstring: str, language: str = "python") -> Dict:
        """
        Generate code from docstring (Copilot-style)
        
        Args:
            docstring: The docstring describing what the code should do
            language: Programming language
        
        Returns:
            Generated code implementation
        """
        generated_code = None
        
        if language.lower() in ["python", "py"]:
            generated_code = self._generate_python_from_docstring(docstring)
        elif language.lower() in ["javascript", "js"]:
            generated_code = self._generate_js_from_docstring(docstring)
        
        return {
            "success": True if generated_code else False,
            "docstring": docstring,
            "language": language,
            "generated_code": generated_code,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_python_from_docstring(self, docstring: str) -> Optional[str]:
        """Generate Python code from docstring"""
        
        # Extract common patterns from docstring
        lower_desc = docstring.lower()
        
        # List operations
        if "list" in lower_desc or "array" in lower_desc:
            if "filter" in lower_desc:
                return """def filter_list(items, condition):
    \"\"\"Filter list based on condition\"\"\"
    return [item for item in items if condition(item)]
"""
            elif "sort" in lower_desc:
                return """def sort_list(items, key=None, reverse=False):
    \"\"\"Sort list\"\"\"
    return sorted(items, key=key, reverse=reverse)
"""
            elif "map" in lower_desc or "transform" in lower_desc:
                return """def transform_list(items, transformer):
    \"\"\"Transform list items\"\"\"
    return [transformer(item) for item in items]
"""
        
        # File operations
        if "file" in lower_desc or "read" in lower_desc:
            if "write" in lower_desc:
                return """def write_file(filename, content):
    \"\"\"Write content to file\"\"\"
    with open(filename, 'w') as f:
        f.write(content)

def read_file(filename):
    \"\"\"Read content from file\"\"\"
    with open(filename, 'r') as f:
        return f.read()
"""
            elif "json" in lower_desc:
                return """import json

def load_json(filename):
    \"\"\"Load JSON from file\"\"\"
    with open(filename, 'r') as f:
        return json.load(f)

def save_json(filename, data):
    \"\"\"Save JSON to file\"\"\"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)
"""
        
        # API operations
        if "api" in lower_desc or "request" in lower_desc or "http" in lower_desc:
            return """import requests
from typing import Dict, Any

def make_request(url: str, method: str = 'GET', **kwargs) -> Dict[str, Any]:
    \"\"\"Make HTTP request\"\"\"
    try:
        response = requests.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json() if response.headers.get('content-type') == 'application/json' else response.text
    except requests.exceptions.RequestException as e:
        raise Exception(f"Request failed: {e}")
"""
        
        # Database operations
        if "database" in lower_desc or "db" in lower_desc:
            return """import sqlite3
from contextlib import contextmanager

class Database:
    def __init__(self, db_name):
        self.db_name = db_name
    
    @contextmanager
    def connection(self):
        conn = sqlite3.connect(self.db_name)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def execute(self, query, params=()):
        with self.connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
"""
        
        return None
    
    def _generate_js_from_docstring(self, docstring: str) -> Optional[str]:
        """Generate JavaScript code from docstring"""
        
        lower_desc = docstring.lower()
        
        # Array operations
        if "array" in lower_desc or "list" in lower_desc:
            if "filter" in lower_desc:
                return """const filterArray = (items, condition) => items.filter(condition);"""
            elif "map" in lower_desc or "transform" in lower_desc:
                return """const transformArray = (items, transformer) => items.map(transformer);"""
        
        # Fetch/HTTP
        if "fetch" in lower_desc or "api" in lower_desc:
            return """async function fetchData(url, options = {}) {
    try {
        const response = await fetch(url, options);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        return await response.json();
    } catch (error) {
        console.error('Fetch error:', error);
        throw error;
    }
}
"""
        
        # Local storage
        if "storage" in lower_desc or "local" in lower_desc:
            return """const storage = {
    set: (key, value) => localStorage.setItem(key, JSON.stringify(value)),
    get: (key) => JSON.parse(localStorage.getItem(key)),
    remove: (key) => localStorage.removeItem(key),
    clear: () => localStorage.clear()
};
"""
        
        return None
    
    def generate_tests(self, function_code: str, language: str = "python") -> Dict:
        """
        Generate test cases for a function
        
        Args:
            function_code: The function to test
            language: Programming language
        
        Returns:
            Test code
        """
        test_code = None
        
        if language.lower() in ["python", "py"]:
            test_code = self._generate_python_tests(function_code)
        elif language.lower() in ["javascript", "js"]:
            test_code = self._generate_js_tests(function_code)
        
        return {
            "success": True if test_code else False,
            "language": language,
            "test_code": test_code,
            "timestamp": datetime.now().isoformat()
        }
    
    def _generate_python_tests(self, function_code: str) -> str:
        """Generate Python unit tests"""
        match = re.search(r'def\s+(\w+)\s*\((.*?)\)', function_code)
        if not match:
            return ""
        
        func_name = match.group(1)
        
        return f"""import unittest
from your_module import {func_name}

class Test{func_name.capitalize()}(unittest.TestCase):
    
    def setUp(self):
        \"\"\"Set up test fixtures\"\"\"
        pass
    
    def test_basic_functionality(self):
        \"\"\"Test basic functionality\"\"\"
        result = {func_name}()
        self.assertIsNotNone(result)
    
    def test_with_valid_input(self):
        \"\"\"Test with valid input\"\"\"
        result = {func_name}()
        self.assertTrue(True)  # Replace with actual assertions
    
    def test_error_handling(self):
        \"\"\"Test error handling\"\"\"
        with self.assertRaises(Exception):
            {func_name}(None)
    
    def tearDown(self):
        \"\"\"Clean up after tests\"\"\"
        pass

if __name__ == '__main__':
    unittest.main()
"""
    
    def _generate_js_tests(self, function_code: str) -> str:
        """Generate JavaScript tests"""
        match = re.search(r'(?:function\s+)?(\w+)\s*\(', function_code)
        if not match:
            return ""
        
        func_name = match.group(1)
        
        return f"""const {{ expect }} = require('chai');
const {{ {func_name} }} = require('./your-module');

describe('{func_name}', () => {{
    
    it('should have basic functionality', () => {{
        const result = {func_name}();
        expect(result).to.exist;
    }});
    
    it('should handle valid input', () => {{
        const result = {func_name}();
        expect(result).to.be.true;
    }});
    
    it('should throw error on invalid input', () => {{
        expect(() => {func_name}(null)).to.throw();
    }});
    
    it('should return expected output', () => {{
        const result = {func_name}();
        expect(result).to.deep.equal({{}});
    }});
}});
"""
    
    def get_suggestions_history(self) -> List[Dict]:
        """Get history of all suggestions made"""
        return self.suggestions_history
    
    def export_suggestions(self, format: str = "json") -> str:
        """
        Export suggestions to file format
        
        Args:
            format: Export format (json, md, txt)
        
        Returns:
            Formatted export string
        """
        if format == "json":
            return json.dumps(self.suggestions_history, indent=2)
        
        elif format == "md":
            text = "# Code Suggestions History\n\n"
            for item in self.suggestions_history:
                text += f"## {item.get('timestamp', 'Unknown')}\n"
                text += f"**Language:** {item.get('language', 'unknown')}\n"
                text += f"**Type:** {item.get('type', 'suggestion')}\n\n"
            return text
        
        else:  # txt
            text = "Code Suggestions History\n"
            text += "=" * 50 + "\n\n"
            for item in self.suggestions_history:
                text += f"Timestamp: {item.get('timestamp', 'Unknown')}\n"
                text += f"Language: {item.get('language', 'unknown')}\n\n"
            return text


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 2: FILE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

class FileGenerator:
    """
    Generates individual files for Python, JavaScript, and other languages
    """
    
    def __init__(self, output_dir: str = "./light_generated_files/"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        self.generation_history = []
    
    def generate_class(self, class_name: str, properties: List[str], methods: List[str], 
                      language: str = "python", filepath: Optional[str] = None) -> Dict:
        """
        Generate a complete class with properties and methods
        """
        content = None
        extension = self._get_extension(language)
        filename = filepath or f"{class_name.lower()}{extension}"
        
        if language.lower() in ["python", "py"]:
            content = self._generate_python_class(class_name, properties, methods)
        elif language.lower() in ["javascript", "js"]:
            content = self._generate_js_class(class_name, properties, methods)
        elif language.lower() in ["typescript", "ts"]:
            content = self._generate_ts_class(class_name, properties, methods)
        elif language.lower() in ["java"]:
            content = self._generate_java_class(class_name, properties, methods)
        
        if not content:
            return {"success": False, "error": f"Unsupported language: {language}"}
        
        filepath = os.path.join(self.output_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        result = {
            "success": True,
            "file_type": "class",
            "class_name": class_name,
            "language": language,
            "filepath": filepath,
            "filename": filename,
            "content": content,
            "size_bytes": len(content),
            "properties": properties,
            "methods": methods,
            "timestamp": datetime.now().isoformat()
        }
        
        self.generation_history.append(result)
        return result
    
    def _generate_python_class(self, class_name: str, properties: List[str], methods: List[str]) -> str:
        """Generate Python class"""
        code = f'''"""
{class_name} class
Auto-generated for {class_name}
"""

class {class_name}:
    """Class for managing {class_name}"""
    
    def __init__(self{''.join(f', {prop}: any' for prop in properties)}):
        """Initialize {class_name}"""
        '''
        
        for prop in properties:
            code += f"\n        self.{prop} = {prop}"
        
        code += "\n    \n    # Properties\n"
        
        for prop in properties:
            code += f'''
    @property
    def {prop}(self):
        """Get {prop}"""
        return self._{prop}
    
    @{prop}.setter
    def {prop}(self, value):
        """Set {prop}"""
        self._{prop} = value
'''
        
        code += "\n    # Methods\n"
        
        for method in methods:
            method_name = method.lower().replace(" ", "_")
            code += f'''
    def {method_name}(self):
        """
        {method}
        """
        pass
'''
        
        code += f'''
    def __str__(self):
        """String representation"""
        return f"{{{class_name}('''
        code += ', '.join(f"{prop}={{self.{prop}}}" for prop in properties)
        code += ''')}"
    
    def __repr__(self):
        """Development representation"""
        return self.__str__()
'''
        
        return code
    
    def _generate_js_class(self, class_name: str, properties: List[str], methods: List[str]) -> str:
        """Generate JavaScript class"""
        code = f"""/**
 * {class_name} class
 * Auto-generated class for {class_name}
 */

class {class_name} {{
    /**
     * Constructor
     * @param {{{', '.join(f'{prop}: any' for prop in properties)}}} options
     */
    constructor({{{''.join(f' {prop},' for prop in properties)[:-1] if properties else ''}}} = {{}}) {{
        """
        
        for prop in properties:
            code += f"\n        this.{prop} = {prop};"
        
        code += "\n    }\n\n"
        
        # Getters and setters
        for prop in properties:
            code += f"""
    get {prop}() {{
        return this._{prop};
    }}
    
    set {prop}(value) {{
        this._{prop} = value;
    }}
"""
        
        # Methods
        code += "    // Methods\n"
        for method in methods:
            method_name = method.lower().replace(" ", "_")
            code += f"""
    {method_name}() {{
        /**
         * {method}
         */
        // Implementation here
    }}
"""
        
        code += f"""
    toString() {{
        return `{class_name}({{{', '.join(f'{prop}: ${{this.{prop}}}' for prop in properties)}}})`;
    }}
}}

module.exports = {class_name};
"""
        
        return code
    
    def _generate_ts_class(self, class_name: str, properties: List[str], methods: List[str]) -> str:
        """Generate TypeScript class"""
        code = f"""/**
 * {class_name} class
 * Auto-generated TypeScript class
 */

interface I{class_name} {{
"""
        
        for prop in properties:
            code += f"\n    {prop}: any;"
        
        code += f"""\n}}

export class {class_name} implements I{class_name} {{
    // Properties
"""
        
        for prop in properties:
            code += f"\n    public {prop}: any;"
        
        code += f"""

    /**
     * Constructor
     */
    constructor({{{''.join(f' {prop},' for prop in properties if properties)[:-1] if properties else ''}}} = {{}}: Partial<I{class_name}>) {{
        """
        
        for prop in properties:
            code += f"\n        this.{prop} = {prop};"
        
        code += "\n    }\n\n"
        
        # Methods
        code += "    // Methods\n"
        for method in methods:
            method_name = method.lower().replace(" ", "_")
            code += f"""
    public {method_name}(): void {{
        /**
         * {method}
         */
        // Implementation here
    }}
"""
        
        code += f"""
    public toString(): string {{
        return `{class_name}({{{', '.join(f'{prop}: ${{this.{prop}}}' for prop in properties)}}})`;
    }}
}}
"""
        
        return code
    
    def _generate_java_class(self, class_name: str, properties: List[str], methods: List[str]) -> str:
        """Generate Java class"""
        code = f"""/**
 * {class_name} class
 * Auto-generated Java class
 */

public class {class_name} {{
    
    // Properties
"""
        
        for prop in properties:
            code += f"\n    private Object {prop};"
        
        code += f"""

    /**
     * Constructor
     */
    public {class_name}("""
        
        code += ", ".join(f"Object {prop}" for prop in properties)
        code += ") {\n"
        
        for prop in properties:
            code += f"        this.{prop} = {prop};\n"
        
        code += "    }\n\n"
        
        # Getters and setters
        for prop in properties:
            prop_upper = prop[0].upper() + prop[1:]
            code += f"""
    public Object get{prop_upper}() {{
        return this.{prop};
    }}
    
    public void set{prop_upper}(Object {prop}) {{
        this.{prop} = {prop};
    }}
"""
        
        # Methods
        code += "    // Methods\n"
        for method in methods:
            method_name = method.lower().replace(" ", "_")
            code += f"""
    public void {method_name}() {{
        /**
         * {method}
         */
        // Implementation here
    }}
"""
        
        code += f"""
    @Override
    public String toString() {{
        return "{class_name}{{"
"""
        
        for i, prop in enumerate(properties):
            if i < len(properties) - 1:
                code += f' + "{prop}=" + this.{prop} + ", "\n            '
            else:
                code += f' + "{prop}=" + this.{prop}'
        
        code += ' + "}}";\n    }\n}\n'
        
        return code
    
    def generate_module(self, module_name: str, exports: List[str], language: str = "python") -> Dict:
        """Generate a module with exports"""
        content = None
        extension = self._get_extension(language)
        filename = f"{module_name.lower()}{extension}"
        
        if language.lower() in ["python", "py"]:
            content = self._generate_python_module(module_name, exports)
        elif language.lower() in ["javascript", "js"]:
            content = self._generate_js_module(module_name, exports)
        
        if not content:
            return {"success": False, "error": f"Unsupported language: {language}"}
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        result = {
            "success": True,
            "file_type": "module",
            "module_name": module_name,
            "language": language,
            "filepath": filepath,
            "filename": filename,
            "exports": exports,
            "timestamp": datetime.now().isoformat()
        }
        
        self.generation_history.append(result)
        return result
    
    def _generate_python_module(self, module_name: str, exports: List[str]) -> str:
        """Generate Python module"""
        code = f'''"""
{module_name} module
Auto-generated module containing utilities and helpers
"""

__version__ = "1.0.0"
__author__ = "LIGHT"

'''
        
        for export in exports:
            code += f'''
def {export}(*args, **kwargs):
    """
    {export} function
    """
    pass

'''
        
        code += f"""__all__ = [{', '.join(f"'{e}'" for e in exports)}]
"""
        
        return code
    
    def _generate_js_module(self, module_name: str, exports: List[str]) -> str:
        """Generate JavaScript module"""
        code = f"""/**
 * {module_name} module
 * Auto-generated module containing utilities and helpers
 */

"""
        
        for export in exports:
            code += f"""
/**
 * {export} function
 */
const {export} = (...args) => {{
    // Implementation
    return null;
}};

"""
        
        code += f"""module.exports = {{
    {', '.join(exports)}
}};
"""
        
        return code
    
    def generate_test_file(self, test_name: str, test_cases: List[str], language: str = "python") -> Dict:
        """Generate a test file with test cases"""
        content = None
        
        if language.lower() in ["python", "py"]:
            content = self._generate_python_tests(test_name, test_cases)
            filename = f"test_{test_name.lower()}.py"
        elif language.lower() in ["javascript", "js"]:
            content = self._generate_js_tests(test_name, test_cases)
            filename = f"{test_name.lower()}.test.js"
        else:
            return {"success": False, "error": f"Unsupported language: {language}"}
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        result = {
            "success": True,
            "file_type": "test",
            "test_name": test_name,
            "language": language,
            "filepath": filepath,
            "filename": filename,
            "test_cases": test_cases,
            "timestamp": datetime.now().isoformat()
        }
        
        self.generation_history.append(result)
        return result
    
    def _generate_python_tests(self, test_name: str, test_cases: List[str]) -> str:
        """Generate Python test file"""
        code = f'''"""
{test_name} tests
Auto-generated test cases
"""

import unittest


class Test{test_name.capitalize()}(unittest.TestCase):
    """Test cases for {test_name}"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def tearDown(self):
        """Clean up after tests"""
        pass
    
'''
        
        for i, test_case in enumerate(test_cases, 1):
            code += f"""
    def test_{i}_{test_case.lower().replace(" ", "_")}(self):
        \"\"\"Test: {test_case}\"\"\"
        self.assertTrue(True)  # Replace with actual test
    
"""
        
        code += """
if __name__ == '__main__':
    unittest.main()
"""
        
        return code
    
    def _generate_js_tests(self, test_name: str, test_cases: List[str]) -> str:
        """Generate JavaScript test file"""
        code = f"""/**
 * {test_name} tests
 * Auto-generated test cases
 */

const {{ expect }} = require('chai');

describe('{test_name}', () => {{
"""
        
        for i, test_case in enumerate(test_cases, 1):
            code += f"""
    it('should {test_case}', () => {{
        expect(true).to.be.true;
    }});
    
"""
        
        code += "});\n"
        
        return code
    
    def generate_config_file(self, config_name: str, settings: Dict, language: str = "python") -> Dict:
        """Generate a configuration file"""
        content = None
        extension = ".yaml" if language == "yaml" else (".json" if language == "json" else ".py")
        filename = f"{config_name.lower()}{extension}"
        
        if language == "json":
            content = json.dumps(settings, indent=2)
        elif language == "yaml":
            content = self._dict_to_yaml(settings)
        elif language == "python":
            content = f"# Configuration file\n\nCONFIG = {settings}\n"
        elif language == "env":
            content = "\n".join(f"{k}={v}" for k, v in settings.items())
            filename = ".env"
        
        if not content:
            return {"success": False, "error": f"Unsupported format: {language}"}
        
        filepath = os.path.join(self.output_dir, filename)
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        result = {
            "success": True,
            "file_type": "config",
            "config_name": config_name,
            "format": language,
            "filepath": filepath,
            "filename": filename,
            "timestamp": datetime.now().isoformat()
        }
        
        self.generation_history.append(result)
        return result
    
    def _dict_to_yaml(self, d: Dict, indent: int = 0) -> str:
        """Convert dict to YAML format"""
        yaml_str = ""
        for key, value in d.items():
            yaml_str += "  " * indent + f"{key}:"
            if isinstance(value, dict):
                yaml_str += "\n" + self._dict_to_yaml(value, indent + 1)
            elif isinstance(value, list):
                yaml_str += "\n"
                for item in value:
                    if isinstance(item, dict):
                        yaml_str += "  " * (indent + 1) + "- " + ", ".join(f"{k}: {v}" for k, v in item.items()) + "\n"
                    else:
                        yaml_str += "  " * (indent + 1) + f"- {item}\n"
            else:
                yaml_str += f" {value}\n"
        return yaml_str
    
    def generate_readme(self, project_name: str, description: str, sections: Dict) -> Dict:
        """Generate a README file"""
        content = f"""# {project_name}

{description}

"""
        
        for section_title, section_content in sections.items():
            content += f"## {section_title}\n\n{section_content}\n\n"
        
        content += """## License

MIT License - Feel free to use this project

---

Generated by LIGHT - AI Code Assistant
"""
        
        filepath = os.path.join(self.output_dir, "README.md")
        
        with open(filepath, 'w') as f:
            f.write(content)
        
        result = {
            "success": True,
            "file_type": "documentation",
            "project_name": project_name,
            "filepath": filepath,
            "filename": "README.md",
            "timestamp": datetime.now().isoformat()
        }
        
        self.generation_history.append(result)
        return result
    
    def _get_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": ".py",
            "py": ".py",
            "javascript": ".js",
            "js": ".js",
            "typescript": ".ts",
            "ts": ".ts",
            "java": ".java",
            "cpp": ".cpp",
            "c": ".c",
            "html": ".html",
            "css": ".css",
            "json": ".json",
            "yaml": ".yaml",
            "sql": ".sql"
        }
        return extensions.get(language.lower(), ".txt")
    
    def list_generated_files(self) -> List[Dict]:
        """List all generated files"""
        for root, dirs, files in os.walk(self.output_dir):
            return [{
                "filename": f,
                "path": os.path.join(root, f),
                "size": os.path.getsize(os.path.join(root, f))
            } for f in files]
    
    def get_generation_history(self) -> List[Dict]:
        """Get generation history"""
        return self.generation_history


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 3: IDE INTEGRATION & EXPORT
# ═══════════════════════════════════════════════════════════════════════════════

class IDEIntegration:
    """
    Handles code export and integration with various IDEs
    """
    
    def __init__(self, export_dir: str = "./light_ide_exports/"):
        self.export_dir = export_dir
        os.makedirs(export_dir, exist_ok=True)
        self.supported_ides = {
            "vscode": "Visual Studio Code",
            "pycharm": "PyCharm",
            "intellij": "IntelliJ IDEA",
            "sublime": "Sublime Text",
            "vim": "Vim/Neovim",
            "emacs": "Emacs",
            "webstorm": "WebStorm",
            "atom": "Atom"
        }
    
    def export_for_vscode(self, project_name: str, files: Dict[str, str], 
                         project_root: Optional[str] = None) -> Dict:
        """
        Export code in VS Code format
        """
        export_path = os.path.join(self.export_dir, f"{project_name}_vscode")
        os.makedirs(export_path, exist_ok=True)
        
        # Create .vscode folder with settings
        vscode_dir = os.path.join(export_path, ".vscode")
        os.makedirs(vscode_dir, exist_ok=True)
        
        # settings.json
        settings = {
            "editor.formatOnSave": True,
            "editor.defaultFormatter": None,
            "python.linting.enabled": True,
            "python.linting.pylintEnabled": True,
            "[python]": {
                "editor.defaultFormatter": "ms-python.python",
                "editor.formatOnSave": True
            },
            "files.exclude": {
                "**/__pycache__": True,
                "**/*.pyc": True,
                "**/node_modules": True
            }
        }
        
        with open(os.path.join(vscode_dir, "settings.json"), 'w') as f:
            json.dump(settings, f, indent=2)
        
        # extensions.json
        extensions = {
            "recommendations": [
                "ms-python.python",
                "ms-python.vscode-pylance",
                "ms-vscode.cpptools",
                "dbaeumer.vscode-eslint",
                "esbenp.prettier-vscode",
                "ms-vscode.extension-pack-for-java"
            ]
        }
        
        with open(os.path.join(vscode_dir, "extensions.json"), 'w') as f:
            json.dump(extensions, f, indent=2)
        
        # launch.json for debugging
        launch = {
            "version": "0.2.0",
            "configurations": [
                {
                    "name": "Python: Current File",
                    "type": "python",
                    "request": "launch",
                    "program": "${file}",
                    "console": "integratedTerminal"
                },
                {
                    "name": "Python: Debug Main",
                    "type": "python",
                    "request": "launch",
                    "program": "${workspaceFolder}/main.py",
                    "console": "integratedTerminal"
                }
            ]
        }
        
        with open(os.path.join(vscode_dir, "launch.json"), 'w') as f:
            json.dump(launch, f, indent=2)
        
        # Create source files
        for filepath, content in files.items():
            full_path = os.path.join(export_path, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create .gitignore
        gitignore = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
env/
venv/
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo

# Environment
.env
.env.local
.env.*.local

# Node
node_modules/
npm-debug.log

# OS
.DS_Store
Thumbs.db
"""
        
        with open(os.path.join(export_path, ".gitignore"), 'w') as f:
            f.write(gitignore)
        
        instructions = f"""
# VS Code Setup Instructions

## 1. Open in VS Code
- File → Open Folder → Select this directory

## 2. Recommended Extensions (Auto-suggested)
The .vscode/extensions.json file will suggest:
- Python extension
- Pylance for advanced Python support
- ESLint for JavaScript
- Prettier for code formatting
- Java Extension Pack

## 3. Setup Virtual Environment (Python Projects)
\`\`\`bash
python -m venv venv
# On Windows:
venv\\Scripts\\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
\`\`\`

## 4. Start Coding
- All files are ready to edit
- Debug configurations are pre-configured in .vscode/launch.json
- Press F5 to start debugging

## 5. Project Structure
{json.dumps({k: '...' for k in files.keys()}, indent=2)}
"""
        
        result = {
            "success": True,
            "ide": "VS Code",
            "project_name": project_name,
            "export_path": export_path,
            "files_created": list(files.keys()),
            "total_files": len(files),
            "vscode_config": True,
            "git_ignore": True,
            "instructions": instructions,
            "setup_command": f"code {export_path}",
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def export_for_pycharm(self, project_name: str, files: Dict[str, str]) -> Dict:
        """
        Export code in PyCharm format
        """
        export_path = os.path.join(self.export_dir, f"{project_name}_pycharm")
        os.makedirs(export_path, exist_ok=True)
        
        # Create .idea folder structure
        idea_dir = os.path.join(export_path, ".idea")
        os.makedirs(idea_dir, exist_ok=True)
        
        # Create project structure file
        project_structure = {
            "name": project_name,
            "type": "PYTHON_MODULE",
            "language_level": "3.10"
        }
        
        with open(os.path.join(idea_dir, "misc.xml"), 'w') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectRootManager" version="2" project-jdk-name="Python 3.10" project-jdk-type="Python SDK" />
</project>
""")
        
        # Create modules.xml
        with open(os.path.join(idea_dir, "modules.xml"), 'w') as f:
            f.write(f"""<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="ProjectModuleManager">
    <modules>
      <module fileurl="file://$PROJECT_DIR$/{project_name}.iml" filepath="$PROJECT_DIR$/{project_name}.iml" />
    </modules>
  </component>
</project>
""")
        
        # Create workspace.xml
        with open(os.path.join(idea_dir, "workspace.xml"), 'w') as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>
<project version="4">
  <component name="RunManager">
    <configuration name="main" type="PythonConfigurationType" factoryName="Python">
      <module name="main" />
      <option name="INTERPRETER_OPTIONS" value="" />
      <option name="PARENT_ENVS" value="true" />
      <option name="SDK_HOME" value="" />
      <option name="WORKING_DIRECTORY" value="$PROJECT_DIR$" />
      <option name="IS_MODULE_SDK" value="true" />
      <option name="ADD_CONTENT_ROOTS" value="true" />
      <option name="ADD_SOURCE_ROOTS" value="true" />
      <option name="SCRIPT_NAME" value="main.py" />
      <method v="2" />
    </configuration>
  </component>
</project>
""")
        
        # Create source files
        for filepath, content in files.items():
            full_path = os.path.join(export_path, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create .iml file
        iml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<module type="PYTHON_MODULE" version="4">
  <component name="NewModuleRootManager">
    <content url="file://$MODULE_DIR$" />
    <orderEntry type="jdk" jdkName="Python 3.10" jdkType="Python SDK" />
    <orderEntry type="sourceFolder" forTests="false" />
  </component>
</module>
"""
        
        with open(os.path.join(export_path, f"{project_name}.iml"), 'w') as f:
            f.write(iml_content)
        
        instructions = f"""
# PyCharm Setup Instructions

## 1. Open Project in PyCharm
- File → Open → Select this directory
- PyCharm will detect the project structure automatically

## 2. Configure Python Interpreter
- PyCharm will prompt you to configure the Python interpreter
- Select your Python 3.10+ installation
- Or create a new virtual environment:
  - Settings → Project → Python Interpreter
  - Click gear icon → Add
  - Select 'New environment'

## 3. Install Dependencies
- PyCharm will detect requirements.txt automatically
- Click "Install requirements" when prompted
- Or run: Right-click requirements.txt → Install All Packages

## 4. Run the Project
- Right-click main.py → Run 'main'
- Or click the green play button next to your code

## 5. Project Layout
- .idea/ → PyCharm configuration
- All your source files are ready to use

## Keyboard Shortcuts
- Run: Shift + F10
- Debug: Shift + F9
- Reformat code: Ctrl + Alt + L (Windows/Linux) or Cmd + Alt + L (Mac)
"""
        
        result = {
            "success": True,
            "ide": "PyCharm",
            "project_name": project_name,
            "export_path": export_path,
            "files_created": list(files.keys()),
            "total_files": len(files),
            "pycharm_config": True,
            "instructions": instructions,
            "open_command": f"pycharm {export_path}",
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def export_for_sublime(self, project_name: str, files: Dict[str, str]) -> Dict:
        """
        Export code in Sublime Text format
        """
        export_path = os.path.join(self.export_dir, f"{project_name}_sublime")
        os.makedirs(export_path, exist_ok=True)
        
        # Create files
        for filepath, content in files.items():
            full_path = os.path.join(export_path, filepath)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'w') as f:
                f.write(content)
        
        # Create .sublime-project file
        project_config = {
            "folders": [
                {
                    "path": ".",
                    "name": project_name,
                    "follow_symlinks": True,
                    "folder_exclude_patterns": [
                        "__pycache__",
                        ".git",
                        "node_modules",
                        ".venv",
                        "venv"
                    ]
                }
            ],
            "settings": {
                "python_interpreter": "/usr/bin/python3",
                "build_systems": [
                    {
                        "name": "Python",
                        "shell_cmd": "python3 $file",
                        "file_regex": "^[ ]*File \"(...*?)\", line ([0-9]*)",
                        "selector": "source.python"
                    }
                ]
            }
        }
        
        with open(os.path.join(export_path, f"{project_name}.sublime-project"), 'w') as f:
            json.dump(project_config, f, indent=2)
        
        result = {
            "success": True,
            "ide": "Sublime Text",
            "project_name": project_name,
            "export_path": export_path,
            "files_created": list(files.keys()),
            "instructions": f"File → Open File → {os.path.join(export_path, f'{project_name}.sublime-project')}",
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def export_as_zip(self, project_name: str, files: Dict[str, str], 
                     include_vscode: bool = True) -> Dict:
        """
        Export entire project as a compressed ZIP file
        """
        zip_path = os.path.join(self.export_dir, f"{project_name}.zip")
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add source files
            for filepath, content in files.items():
                zipf.writestr(filepath, content)
            
            # Add VS Code config if requested
            if include_vscode:
                settings = {
                    "editor.formatOnSave": True,
                    "[python]": {"editor.defaultFormatter": "ms-python.python"}
                }
                zipf.writestr(".vscode/settings.json", json.dumps(settings, indent=2))
                
                extensions = {"recommendations": ["ms-python.python"]}
                zipf.writestr(".vscode/extensions.json", json.dumps(extensions, indent=2))
        
        result = {
            "success": True,
            "project_name": project_name,
            "zip_path": zip_path,
            "file_size_bytes": os.path.getsize(zip_path),
            "total_files": len(files),
            "instructions": f"Extract {zip_path} to use the project",
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def export_as_markdown(self, project_name: str, files: Dict[str, str]) -> Dict:
        """
        Export code as single Markdown file for documentation
        """
        md_path = os.path.join(self.export_dir, f"{project_name}_code.md")
        
        markdown_content = f"""# {project_name} - Complete Code

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Table of Contents

"""
        
        # Create table of contents
        for filepath in files.keys():
            section = filepath.replace('/', ' → ')
            markdown_content += f"- [{section}](#{filepath.replace('/', '-').replace('.', '-')})\n"
        
        markdown_content += "\n---\n\n"
        
        # Add all files as code blocks
        for filepath, content in files.items():
            # Determine language for code highlighting
            ext = filepath.split('.')[-1] if '.' in filepath else 'text'
            language_map = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'typescript',
                'java': 'java',
                'cpp': 'cpp',
                'c': 'c',
                'html': 'html',
                'css': 'css',
                'json': 'json',
                'yaml': 'yaml',
                'sql': 'sql'
            }
            language = language_map.get(ext, ext)
            
            markdown_content += f"## {filepath}\n\n```{language}\n{content}\n```\n\n"
        
        with open(md_path, 'w') as f:
            f.write(markdown_content)
        
        result = {
            "success": True,
            "project_name": project_name,
            "markdown_path": md_path,
            "file_size_bytes": os.path.getsize(md_path),
            "instructions": f"View {md_path} in any markdown viewer or GitHub",
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def create_copy_paste_bundle(self, project_name: str, files: Dict[str, str]) -> Dict:
        """
        Create human-readable file bundle for easy copy-paste into IDEs
        """
        bundle_path = os.path.join(self.export_dir, f"{project_name}_copy_paste.txt")
        
        content = f"""
{'='*80}
{project_name.upper()} - COPY-PASTE BUNDLE
{'='*80}

This file contains all your code files. You can copy each section below and
create files with the specified names in your IDE.

Instructions:
1. Open your IDE (VS Code, PyCharm, Sublime, etc.)
2. Create files with the exact names shown below
3. Copy the code from each section into the corresponding file
4. Save and run!

{'='*80}

"""
        
        for filepath, code in files.items():
            content += f"""
╔{'='*78}╗
║ FILE: {filepath:<74}║
╚{'='*78}╝

{code}

{'─'*80}

"""
        
        content += f"""
{'='*80}
END OF {project_name.upper()}
{'='*80}

Total Files: {len(files)}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Generator: LIGHT - Voice-Based Code Assistant

For Next Steps:
- Run setup scripts (setup.bat on Windows, setup.sh on Mac/Linux)
- Install dependencies: pip install -r requirements.txt (Python)
- Start developing!

"""
        
        with open(bundle_path, 'w') as f:
            f.write(content)
        
        result = {
            "success": True,
            "project_name": project_name,
            "bundle_path": bundle_path,
            "total_files": len(files),
            "instructions": f"Open {bundle_path} and copy sections into your IDE",
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def get_export_formats(self) -> Dict:
        """Get all available export formats"""
        return {
            "vscode": "VS Code - Recommended for all languages",
            "pycharm": "PyCharm - Best for Python development",
            "sublime": "Sublime Text - Lightweight text editor",
            "vim": "Vim - Terminal-based editor",
            "webstorm": "WebStorm - JavaScript/Web development",
            "zip": "ZIP Archive - Portable project format",
            "markdown": "Markdown - Documentation format",
            "copy_paste": "Copy-Paste Bundle - Plain text, manual IDE setup"
        }


# ═══════════════════════════════════════════════════════════════════════════════
# SECTION 4: PROJECT CODE GENERATION
# ═══════════════════════════════════════════════════════════════════════════════

class CodeGenerator:
    """
    Advanced code generation system for LIGHT.
    
    Generates complete, production-ready projects with:
    - Multiple coordinated files
    - Proper project structure
    - Configuration and dependencies
    - Installation instructions
    - Everything ready to run immediately
    """
    
    def __init__(self, output_dir: str = "./light_generated_projects/"):
        self.output_dir = output_dir
        self.project_history = []
        os.makedirs(output_dir, exist_ok=True)
        self.load_history()
    
    def load_history(self):
        """Load project generation history"""
        history_file = os.path.join(self.output_dir, "generation_history.json")
        if os.path.exists(history_file):
            try:
                with open(history_file, 'r') as f:
                    self.project_history = json.load(f)
            except:
                self.project_history = []
    
    def save_history(self):
        """Save project generation history"""
        history_file = os.path.join(self.output_dir, "generation_history.json")
        with open(history_file, 'w') as f:
            json.dump(self.project_history, f, indent=2)
    
    def generate_python_project(self, 
                               project_name: str,
                               description: str,
                               features: List[str]) -> Dict:
        """Generate a complete Python project"""
        project_path = os.path.join(self.output_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        files_created = {}
        
        # Main application file
        main_content = self._generate_python_main(project_name, description, features)
        main_file = os.path.join(project_path, "main.py")
        with open(main_file, 'w') as f:
            f.write(main_content)
        files_created["main.py"] = main_content
        
        # Requirements file
        requirements = self._generate_requirements(features)
        req_file = os.path.join(project_path, "requirements.txt")
        with open(req_file, 'w') as f:
            f.write(requirements)
        files_created["requirements.txt"] = requirements
        
        # Config file
        config_content = self._generate_config(project_name, features)
        config_file = os.path.join(project_path, "config.yaml")
        with open(config_file, 'w') as f:
            f.write(config_content)
        files_created["config.yaml"] = config_content
        
        # README
        readme = self._generate_readme_python(project_name, description, features)
        readme_file = os.path.join(project_path, "README.md")
        with open(readme_file, 'w') as f:
            f.write(readme)
        files_created["README.md"] = readme
        
        # Utils module if needed
        if any(f in features for f in ["database", "api", "logging", "utilities"]):
            utils_content = self._generate_utils_module()
            utils_file = os.path.join(project_path, "utils.py")
            with open(utils_file, 'w') as f:
                f.write(utils_content)
            files_created["utils.py"] = utils_content
        
        # Setup script
        setup_script = self._generate_setup_script("python")
        setup_file = os.path.join(project_path, "setup.bat")
        with open(setup_file, 'w') as f:
            f.write(setup_script)
        files_created["setup.bat"] = setup_script
        
        # Run script
        run_script = self._generate_run_script("python", "python main.py")
        run_file = os.path.join(project_path, "run.bat")
        with open(run_file, 'w') as f:
            f.write(run_script)
        files_created["run.bat"] = run_script
        
        result = {
            "status": "✅ SUCCESS",
            "project_name": project_name,
            "project_path": os.path.abspath(project_path),
            "project_type": "Python",
            "files_created": list(files_created.keys()),
            "total_files": len(files_created),
            "timestamp": datetime.now().isoformat(),
            "setup_instructions": [
                "1. Navigate to: " + os.path.abspath(project_path),
                "2. Run: setup.bat (Windows) or bash setup.sh (Mac/Linux)",
                "3. Run: python main.py",
            ],
            "features": features
        }
        
        self.project_history.append(result)
        self.save_history()
        
        return result
    
    def generate_fullstack_project(self,
                                  project_name: str,
                                  frontend: str = "react",
                                  backend: str = "node",
                                  description: str = "") -> Dict:
        """Generate a complete full-stack application"""
        project_path = os.path.join(self.output_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        files_created = {}
        
        # Create frontend folder
        frontend_path = os.path.join(project_path, "frontend")
        os.makedirs(frontend_path, exist_ok=True)
        
        # Create backend folder
        backend_path = os.path.join(project_path, "backend")
        os.makedirs(backend_path, exist_ok=True)
        
        # Generate frontend
        if frontend.lower() == "react":
            frontend_files = self._generate_react_app(frontend_path, project_name)
            files_created.update(frontend_files)
        
        # Generate backend
        if backend.lower() == "node":
            backend_files = self._generate_node_backend(backend_path, project_name)
            files_created.update(backend_files)
        elif backend.lower() == "python":
            backend_files = self._generate_python_backend(backend_path, project_name)
            files_created.update(backend_files)
        
        # Create docker-compose
        docker_compose = self._generate_docker_compose(project_name, frontend, backend)
        dc_file = os.path.join(project_path, "docker-compose.yml")
        with open(dc_file, 'w') as f:
            f.write(docker_compose)
        files_created["docker-compose.yml"] = docker_compose
        
        # Create README
        readme = self._generate_fullstack_readme(project_name, frontend, backend, description)
        readme_file = os.path.join(project_path, "README.md")
        with open(readme_file, 'w') as f:
            f.write(readme)
        files_created["README.md"] = readme
        
        result = {
            "status": "✅ FULL-STACK PROJECT CREATED",
            "project_name": project_name,
            "project_path": os.path.abspath(project_path),
            "frontend": frontend,
            "backend": backend,
            "files_created": list(files_created.keys()),
            "structure": {
                "frontend": os.path.abspath(frontend_path),
                "backend": os.path.abspath(backend_path),
            },
            "setup_instructions": [
                f"Terminal 1: cd frontend && npm install && npm start",
                f"Terminal 2: cd backend && npm install && npm start",
                f"Or use Docker: docker-compose up",
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        self.project_history.append(result)
        self.save_history()
        
        return result
    
    def generate_web_app(self,
                        project_name: str,
                        app_type: str = "dashboard",
                        features: List[str] = None) -> Dict:
        """Generate a web application"""
        project_path = os.path.join(self.output_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        if features is None:
            features = ["responsive", "dark_theme", "charts"]
        
        files_created = {}
        
        # Create folders
        css_path = os.path.join(project_path, "css")
        js_path = os.path.join(project_path, "js")
        os.makedirs(css_path, exist_ok=True)
        os.makedirs(js_path, exist_ok=True)
        
        # HTML
        html_content = self._generate_html_template(project_name, app_type, features)
        html_file = os.path.join(project_path, "index.html")
        with open(html_file, 'w') as f:
            f.write(html_content)
        files_created["index.html"] = html_content
        
        # CSS
        css_content = self._generate_css_stylesheet(app_type, features)
        css_file = os.path.join(css_path, "style.css")
        with open(css_file, 'w') as f:
            f.write(css_content)
        files_created["css/style.css"] = css_content
        
        # JavaScript
        js_content = self._generate_javascript(app_type, features)
        js_file = os.path.join(js_path, "app.js")
        with open(js_file, 'w') as f:
            f.write(js_content)
        files_created["js/app.js"] = js_content
        
        result = {
            "status": "✅ WEB APP CREATED",
            "project_name": project_name,
            "project_path": os.path.abspath(project_path),
            "app_type": app_type,
            "files_created": list(files_created.keys()),
            "launch_instructions": [
                f"Open: {html_file}",
                "Or start a local server: python -m http.server 8000",
                "Then visit: http://localhost:8000",
            ],
            "features": features,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def generate_api_server(self,
                           project_name: str,
                           framework: str = "flask",
                           endpoints: List[str] = None) -> Dict:
        """Generate a REST API server"""
        project_path = os.path.join(self.output_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        if endpoints is None:
            endpoints = ["GET /api/health", "GET /api/data", "POST /api/create"]
        
        files_created = {}
        
        if framework.lower() == "flask":
            app_content = self._generate_flask_api(project_name, endpoints)
            app_file = os.path.join(project_path, "app.py")
            with open(app_file, 'w') as f:
                f.write(app_content)
            files_created["app.py"] = app_content
            
            requirements = self._generate_api_requirements("flask", endpoints)
            req_file = os.path.join(project_path, "requirements.txt")
            with open(req_file, 'w') as f:
                f.write(requirements)
            files_created["requirements.txt"] = requirements
        
        elif framework.lower() == "express":
            app_content = self._generate_express_api(project_name, endpoints)
            app_file = os.path.join(project_path, "server.js")
            with open(app_file, 'w') as f:
                f.write(app_content)
            files_created["server.js"] = app_content
        
        result = {
            "status": "✅ API SERVER CREATED",
            "project_name": project_name,
            "project_path": os.path.abspath(project_path),
            "framework": framework,
            "endpoints": endpoints,
            "files_created": list(files_created.keys()),
            "startup_instructions": [
                f"1. cd {project_name}",
                "2. pip install -r requirements.txt",
                "3. python app.py",
                "4. API at http://localhost:5000",
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def generate_database_project(self,
                                 project_name: str,
                                 db_type: str = "sqlite",
                                 tables: List[str] = None) -> Dict:
        """Generate a database project"""
        project_path = os.path.join(self.output_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        if tables is None:
            tables = ["users", "products", "orders"]
        
        files_created = {}
        
        # Schema
        schema_sql = self._generate_database_schema(tables, db_type)
        schema_file = os.path.join(project_path, "schema.sql")
        with open(schema_file, 'w') as f:
            f.write(schema_sql)
        files_created["schema.sql"] = schema_sql
        
        # Database manager
        db_manager = self._generate_db_manager(project_name, tables)
        db_file = os.path.join(project_path, "database.py")
        with open(db_file, 'w') as f:
            f.write(db_manager)
        files_created["database.py"] = db_manager
        
        # Test data
        test_data = self._generate_test_data_script(tables)
        test_file = os.path.join(project_path, "seed_data.py")
        with open(test_file, 'w') as f:
            f.write(test_data)
        files_created["seed_data.py"] = test_data
        
        result = {
            "status": "✅ DATABASE PROJECT CREATED",
            "project_name": project_name,
            "project_path": os.path.abspath(project_path),
            "database_type": db_type,
            "tables": tables,
            "files_created": list(files_created.keys()),
            "setup_instructions": [
                f"1. cd {project_name}",
                "2. python database.py",
                "3. python seed_data.py",
                "4. Database ready!",
            ],
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    # ==================== GENERATOR TEMPLATES ====================
    
    def _generate_python_main(self, name: str, desc: str, features: List[str]) -> str:
        """Generate main Python file"""
        features_str = "\n".join(f"  - {f}" for f in features)
        return f'''#!/usr/bin/env python3
"""
{name.upper()}
Description: {desc}

Features:
{features_str}

Usage:
    python main.py
"""

import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class {name.title()}:
    """Main application class"""
    
    def __init__(self):
        logger.info(f"Initializing {name}...")
        self.started_at = datetime.now()
    
    def run(self):
        """Run the application"""
        logger.info("Starting application")
        try:
            self.main_loop()
        except KeyboardInterrupt:
            logger.info("Interrupted by user")
        finally:
            self.cleanup()
    
    def main_loop(self):
        """Main loop"""
        while True:
            try:
                user_input = input("\\n> ").strip()
                if user_input.lower() in ['exit', 'quit']:
                    break
                if user_input:
                    self.process_command(user_input)
            except KeyboardInterrupt:
                break
    
    def process_command(self, command: str):
        """Process command"""
        logger.info(f"Processing: {{command}}")
        print(f"✅ Command: {{command}}")
    
    def cleanup(self):
        """Cleanup"""
        logger.info("Cleanup complete")


if __name__ == "__main__":
    app = {name.title()}()
    app.run()
'''
    
    def _generate_requirements(self, features: List[str]) -> str:
        """Generate requirements.txt"""
        base = ["pyyaml>=6.0"]
        feature_deps = {
            "database": ["sqlalchemy>=2.0"],
            "api": ["requests>=2.28"],
            "web": ["flask>=2.3"],
            "data": ["pandas>=1.5"],
            "logging": ["python-logging-loki>=0.3"],
        }
        deps = set(base)
        for feat in features:
            if feat in feature_deps:
                deps.update(feature_deps[feat])
        return "\n".join(sorted(deps)) + "\n"
    
    def _generate_config(self, name: str, features: List[str]) -> str:
        """Generate config.yaml"""
        features_yaml = "\n".join(f"  {f}: true" for f in features)
        return f'''app:
  name: {name}
  version: 1.0.0
  debug: false

features:
{features_yaml}

database:
  type: sqlite
  path: ./data.db
'''
    
    def _generate_readme_python(self, name: str, desc: str, features: List[str]) -> str:
        """Generate README"""
        features_md = "\n".join(f"- {f}" for f in features)
        return f'''# {name.upper()}

{desc}

## Features
{features_md}

## Installation

```bash
python -m venv venv
# Windows: venv\\Scripts\\activate
# Mac/Linux: source venv/bin/activate

pip install -r requirements.txt
```

## Usage

```bash
python main.py
```

---
Generated by LIGHT Code Generator
'''
    
    def _generate_utils_module(self) -> str:
        """Generate utils module"""
        return '''"""Utility functions"""

import logging
import json

logger = logging.getLogger(__name__)

def log_info(msg):
    logger.info(msg)
    print(f"ℹ️  {msg}")

def log_error(msg):
    logger.error(msg)
    print(f"❌ {msg}")

def load_json(filepath):
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Failed to load {filepath}")
        return None
'''
    
    def _generate_setup_script(self, lang: str) -> str:
        """Generate setup script"""
        if lang == "python":
            return '''@echo off
echo Setting up Python environment...
python -m venv venv
call venv\\Scripts\\activate.bat
pip install -r requirements.txt
echo Setup complete!
pause
'''
        return ""
    
    def _generate_run_script(self, lang: str, cmd: str) -> str:
        """Generate run script"""
        if lang == "python":
            return f'''@echo off
call venv\\Scripts\\activate.bat
{cmd}
pause
'''
        return ""
    
    def _generate_react_app(self, path: str, name: str) -> Dict:
        """Generate React app"""
        files = {}
        package_json = {
            "name": f"{name}-frontend",
            "version": "1.0.0",
            "dependencies": {
                "react": "^18.0.0",
                "react-dom": "^18.0.0"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }
        package_file = os.path.join(path, "package.json")
        with open(package_file, 'w') as f:
            json.dump(package_json, f, indent=2)
        files["frontend/package.json"] = json.dumps(package_json, indent=2)
        return files
    
    def _generate_node_backend(self, path: str, name: str) -> Dict:
        """Generate Node backend"""
        files = {}
        server_js = f'''const express = require('express');
const app = express();

app.get('/api/health', (req, res) => {{
  res.json({{ status: 'OK' }});
}});

app.listen(5000, () => {{
  console.log('Server running on :5000');
}});
'''
        server_file = os.path.join(path, "server.js")
        with open(server_file, 'w') as f:
            f.write(server_js)
        files["backend/server.js"] = server_js
        return files
    
    def _generate_python_backend(self, path: str, name: str) -> Dict:
        """Generate Python backend"""
        files = {}
        app_py = f'''from flask import Flask
app = Flask(__name__)

@app.route('/api/health')
def health():
    return {{"status": "OK"}}

if __name__ == '__main__':
    app.run(debug=True, port=5000)
'''
        app_file = os.path.join(path, "app.py")
        with open(app_file, 'w') as f:
            f.write(app_py)
        files["backend/app.py"] = app_py
        return files
    
    def _generate_docker_compose(self, name: str, frontend: str, backend: str) -> str:
        """Generate docker-compose"""
        return f'''version: '3.8'
services:
  frontend:
    ports:
      - "3000:3000"
  backend:
    ports:
      - "5000:5000"
'''
    
    def _generate_fullstack_readme(self, name: str, frontend: str, backend: str, desc: str) -> str:
        """Generate fullstack README"""
        return f'''# {name}

{desc}

Frontend: {frontend}
Backend: {backend}

## Quick Start

```bash
cd frontend && npm install && npm start
# In another terminal:
cd backend && npm install && npm start
```

Or use Docker:
```bash
docker-compose up
```

Ready to run!
'''
    
    def _generate_html_template(self, name: str, app_type: str, features: List[str]) -> str:
        """Generate HTML"""
        features_html = "\n".join(f"<li>{f}</li>" for f in features)
        return f'''<!DOCTYPE html>
<html>
<head>
  <title>{name}</title>
  <link rel="stylesheet" href="css/style.css">
</head>
<body>
  <h1>{name}</h1>
  <ul>{features_html}</ul>
  <script src="js/app.js"></script>
</body>
</html>
'''
    
    def _generate_css_stylesheet(self, app_type: str, features: List[str]) -> str:
        """Generate CSS"""
        return '''* { margin: 0; padding: 0; }
body { font-family: Arial; background: #f4f4f4; }
h1 { color: #333; margin: 20px; }
'''
    
    def _generate_javascript(self, app_type: str, features: List[str]) -> str:
        """Generate JavaScript"""
        return '''console.log("App loaded");
window.app = {};
'''
    
    def _generate_flask_api(self, name: str, endpoints: List[str]) -> str:
        """Generate Flask API"""
        endpoint_code = "\n".join([f"@app.route('{ep.split()[1]}')\ndef handle(): return {{'status': 'ok'}}" for ep in endpoints])
        return f'''from flask import Flask
app = Flask(__name__)

{endpoint_code}

if __name__ == '__main__':
    app.run(debug=True)
'''
    
    def _generate_express_api(self, name: str, endpoints: List[str]) -> str:
        """Generate Express API"""
        return f'''const express = require('express');
const app = express();

app.get('/api/health', (req, res) => {{
  res.json({{ status: 'ok' }});
}});

app.listen(5000);
'''
    
    def _generate_database_schema(self, tables: List[str], db_type: str) -> str:
        """Generate schema"""
        return "\n".join([f"CREATE TABLE {t} (id INTEGER PRIMARY KEY);" for t in tables])
    
    def _generate_db_manager(self, name: str, tables: List[str]) -> str:
        """Generate DB manager"""
        return '''import sqlite3

class DatabaseManager:
    def __init__(self, db_path="database.db"):
        self.db_path = db_path
    
    def execute(self, query):
        with sqlite3.connect(self.db_path) as conn:
            return conn.execute(query)
'''
    
    def _generate_test_data_script(self, tables: List[str]) -> str:
        """Generate test data"""
        return '''"""Seed test data"""

def seed():
    print("Seeding data...")
    print("Done!")

if __name__ == "__main__":
    seed()
'''
    
    def _generate_api_requirements(self, framework: str, endpoints: List[str]) -> str:
        """Generate API requirements"""
        if framework.lower() == "flask":
            return "flask>=2.3\nflask-cors>=4.0\n"
        return "express\n"


# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR VOICE COMMAND PROCESSING
# ═══════════════════════════════════════════════════════════════════════════════

def generate_project_from_voice_command(command: str, gen: CodeGenerator) -> Dict:
    """Parse voice command and generate appropriate project"""
    command_lower = command.lower()
    
    if "python" in command_lower and "fullstack" not in command_lower:
        name = extract_project_name(command)
        features = extract_features(command)
        return gen.generate_python_project(name, "Generated by LIGHT", features)
    
    elif "react" in command_lower or "fullstack" in command_lower:
        name = extract_project_name(command)
        frontend = "react" if "react" in command_lower else "vue"
        backend = "node" if "node" in command_lower else "python"
        return gen.generate_fullstack_project(name, frontend, backend)
    
    elif any(w in command_lower for w in ["web", "html", "dashboard"]):
        name = extract_project_name(command)
        app_type = "dashboard" if "dashboard" in command_lower else "website"
        return gen.generate_web_app(name, app_type)
    
    elif "api" in command_lower:
        name = extract_project_name(command)
        framework = "flask" if "flask" in command_lower else "express"
        return gen.generate_api_server(name, framework)
    
    elif "database" in command_lower:
        name = extract_project_name(command)
        return gen.generate_database_project(name)
    
    else:
        name = extract_project_name(command) or "my_project"
        return gen.generate_python_project(name, "Generated by LIGHT", [])


def extract_project_name(command: str) -> str:
    """Extract project name from voice command"""
    match = re.search(r"(?:project|app|system|called|named)\s+(\w+)", command, re.IGNORECASE)
    if match:
        name = match.group(1)
        if len(name) > 3:
            return name.lower()
    return "generated_project"


def extract_features(command: str) -> List[str]:
    """Extract features from voice command"""
    feature_keywords = {
        "database": ["database", "sql", "db"],
        "api": ["api", "rest"],
        "web": ["web", "html"],
        "logging": ["logging", "logs"],
        "data": ["data", "pandas"],
    }
    
    command_lower = command.lower()
    features = []
    
    for feature, keywords in feature_keywords.items():
        if any(kw in command_lower for kw in keywords):
            features.append(feature)
    
    return features if features else ["basic"]
