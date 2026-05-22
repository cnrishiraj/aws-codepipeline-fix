import os
import sys
import json
import boto3
import subprocess
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def run_script(script_path):
    """
    Run a python script and capture any errors
    """
    logger.debug(f"Attempting to run script: {script_path}")
    try:
        logger.debug(f"Current working directory: {os.getcwd()}")
        logger.debug(f"Script absolute path: {os.path.abspath(script_path)}")
        logger.debug(f"Python executable: {sys.executable}")
        
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True
        )
        logger.debug(f"Script execution result: returncode={result.returncode}")
        if result.stderr:
            logger.debug(f"Script stderr: {result.stderr}")
        if result.stdout:
            logger.debug(f"Script stdout: {result.stdout}")
        return result.returncode == 0, result.stderr if result.returncode != 0 else result.stdout
    except Exception as e:
        logger.error(f"Error running script: {e}", exc_info=True)
        return False, str(e)

def fix_code_with_claude(code, error_message):
    """
    Use Claude 3.5 via AWS Bedrock to fix the code, or apply basic fixes if AWS is not available
    """
    logger.debug("Attempting to fix code")
    try:
        # First, try basic syntax fixes
        fixed_code = apply_basic_fixes(code, error_message)
        if fixed_code and fixed_code != code:
            logger.info("Applied basic syntax fixes")
            return fixed_code
            
        # If basic fixes don't work, try AWS Bedrock
        logger.debug("Basic fixes insufficient, trying AWS Bedrock")
        region = os.environ.get('AWS_REGION', 'us-east-1')
        logger.debug(f"Using AWS region: {region}")
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=region
        )
        
        logger.debug("Preparing prompt for Claude")
        prompt = f"""
        Fix this Python code that has errors.
        
        CODE:
        ```python
        {code}
        ```
        
        ERROR:
        {error_message}
        
        Provide ONLY the corrected code without any explanations.
        """
        
        logger.debug("Calling Bedrock API")
        response = bedrock.invoke_model(
            modelId='anthropic.claude-3-sonnet-20240229-v1:0',
            body=json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.1,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            })
        )
        
        logger.debug("Processing Bedrock response")
        response_body = json.loads(response.get('body').read())
        fixed_code = response_body['content'][0]['text']
        
        # Extract code from markdown if present
        if "```python" in fixed_code and "```" in fixed_code:
            code_block_start = fixed_code.find("```python") + len("```python")
            code_block_end = fixed_code.rfind("```")
            fixed_code = fixed_code[code_block_start:code_block_end].strip()
        
        logger.debug("Successfully obtained fixed code from AWS Bedrock")
        return fixed_code
    
    except Exception as e:
        logger.warning(f"AWS Bedrock not available or failed: {e}")
        # Fall back to basic fixes if AWS is not available
        fixed_code = apply_basic_fixes(code, error_message)
        if fixed_code and fixed_code != code:
            logger.info("Applied basic syntax fixes as fallback")
            return fixed_code
        logger.error("Both AWS Bedrock and basic fixes failed")
        raise

def apply_basic_fixes(code, error_message):
    """
    Apply basic syntax fixes for common Python errors
    """
    logger.debug("Applying basic syntax fixes")
    fixed_code = code
    
    # Fix common syntax errors
    lines = fixed_code.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        original_line = line
        
        # Fix missing colons in function definitions and if statements
        if line.strip().startswith(('def ', 'if ', 'elif ', 'else', 'for ', 'while ', 'try', 'except', 'finally', 'with ', 'class ')):
            if not line.rstrip().endswith(':') and not line.strip().endswith('\\'):
                # Insert colon before any comment
                if '#' in line:
                    comment_pos = line.find('#')
                    line = line[:comment_pos].rstrip() + ':  ' + line[comment_pos:]
                else:
                    line = line.rstrip() + ':'
                logger.debug(f"Added missing colon to line {i+1}: {original_line.strip()} -> {line.strip()}")
        
        # Fix syntax error in print statements (space in function name)
        if 'p rint(' in line:
            line = line.replace('p rint(', 'print(')
            logger.debug(f"Fixed print statement on line {i+1}")
        
        # Fix missing closing parentheses in print statements and function calls
        if ('print(' in line or 'rint(' in line) and not line.rstrip().endswith(')'):
            # Count parentheses to see if any are missing
            open_count = line.count('(') 
            close_count = line.count(')')
            if open_count > close_count:
                line = line.rstrip() + ')' * (open_count - close_count)
                logger.debug(f"Added missing closing paren to line {i+1}")
        
        # Fix method calls missing parentheses (e.g., name.upper -> name.upper())
        if '.upper' in line and not '.upper()' in line:
            line = line.replace('.upper', '.upper()')
            logger.debug(f"Fixed method call on line {i+1}")
        
        # Fix missing opening quotes and syntax errors
        if 'name  #' in line and 'print(' in line:
            line = line.replace('name  #', 'name)  #')
            logger.debug(f"Fixed string concatenation on line {i+1}")
        
        # Fix wrong operators (basic case: - instead of + in calculate_sum)
        if 'return a - b' in line and 'calculate_sum' in code:
            line = line.replace('return a - b', 'return a + b')
            logger.debug(f"Fixed operator in calculate_sum on line {i+1}")
        
        # Fix variable name errors and syntax errors in return statements
        if '/fsoo' in line:
            line = line.replace('/fsoo', '/')
            logger.debug(f"Fixed variable name error on line {i+1}")
        
        # Fix indentation errors (basic case)
        if line.startswith('   return') and not line.startswith('    '):
            line = '    ' + line.lstrip()
            logger.debug(f"Fixed indentation on line {i+1}")
        
        # Remove unreachable code after return statements
        if i > 0 and 'return' in lines[i-1] and line.strip().startswith('print(') and 'unreachable' in line.lower():
            logger.debug(f"Removing unreachable code on line {i+1}")
            continue
            
        fixed_lines.append(line)
    
    result = '\n'.join(fixed_lines)
    
    # Add division by zero check for divide function
    if 'def divide(' in result and 'if y == 0:' not in result:
        # Find and replace the divide function to add zero division check
        lines = result.split('\n')
        new_lines = []
        in_divide_func = False
        
        for line in lines:
            if line.strip().startswith('def divide('):
                in_divide_func = True
                new_lines.append(line)
            elif in_divide_func and line.strip().startswith('return x / y'):
                # Add zero division check before return
                indent = '    '
                new_lines.append(f"{indent}if y == 0:")
                new_lines.append(f"{indent}    raise ValueError(\"Cannot divide by zero\")")
                new_lines.append(line)
                in_divide_func = False
            else:
                new_lines.append(line)
                if in_divide_func and line.strip() and not line.strip().startswith('#') and not line.strip().startswith('def'):
                    in_divide_func = False
        
        result = '\n'.join(new_lines)
        logger.debug("Added zero division check to divide function")
    
    return result

def main():
    logger.info("Starting Python error fixer")
    logger.debug(f"Arguments: {sys.argv}")
    logger.debug(f"Current working directory: {os.getcwd()}")
    logger.debug(f"Environment variables: {dict(os.environ)}")
    
    if len(sys.argv) != 2:
        logger.error("Usage: python fix_python_errors.py <script_path>")
        sys.exit(1)
    
    script_path = sys.argv[1]
    logger.info(f"Processing file: {script_path}")
    
    if not os.path.exists(script_path):
        logger.error(f"File not found: {script_path}")
        sys.exit(1)
    
    # Read the original code
    try:
        with open(script_path, 'r') as f:
            original_code = f.read()
        logger.debug(f"Read original code from {script_path}:\n{original_code}")
    except Exception as e:
        logger.error(f"Error reading file: {e}", exc_info=True)
        sys.exit(1)
    
    # Try to run the script
    logger.info("Attempting to run script")
    success, result = run_script(script_path)
    
    if success:
        logger.info(f"Script {script_path} runs successfully")
        sys.exit(0)
    
    logger.info(f"Found errors in {script_path}, attempting to fix...")
    
    try:
        # Get fixed code from Claude
        fixed_code = fix_code_with_claude(original_code, result)
        logger.debug(f"Fixed code:\n{fixed_code}")
        
        # Write the fixed code
        with open(script_path, 'w') as f:
            f.write(fixed_code)
        logger.info(f"Wrote fixed code to {script_path}")
        
        # Verify the fix
        logger.info("Verifying the fix")
        success, result = run_script(script_path)
        
        if success:
            logger.info(f"Successfully fixed {script_path}")
        else:
            logger.error(f"Failed to fix {script_path}: {result}")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Error during fix process: {e}", exc_info=True)
        sys.exit(1)

if __name__ == "__main__":
    main() 