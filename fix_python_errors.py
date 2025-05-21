import os
import sys
import json
import boto3
import subprocess
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_script(script_path):
    """
    Run a python script and capture any errors
    """
    logger.debug(f"Attempting to run script: {script_path}")
    try:
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
        logger.error(f"Error running script: {e}")
        return False, str(e)

def fix_code_with_claude(code, error_message):
    """
    Use Claude 3.5 via AWS Bedrock to fix the code
    """
    logger.debug("Initializing Bedrock client")
    try:
        bedrock = boto3.client(
            service_name='bedrock-runtime',
            region_name=os.environ.get('AWS_REGION', 'us-east-1')
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
        
        logger.debug("Successfully obtained fixed code")
        return fixed_code
    
    except Exception as e:
        logger.error(f"Error calling Claude: {e}", exc_info=True)
        raise

def main():
    logger.info("Starting Python error fixer")
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
        logger.debug(f"Read original code from {script_path}")
    except Exception as e:
        logger.error(f"Error reading file: {e}")
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