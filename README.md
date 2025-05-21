# Python Error Fixer with AWS CodePipeline and Claude

Automatically fixes Python errors in your code using AWS CodePipeline and Claude 3.5 (AWS Bedrock).

## Files

- `fix_python_errors.py`: Script that uses Claude 3.5 to detect and fix Python errors
- `buildspec.yml`: AWS CodeBuild configuration
- `broken_script.py`: Sample Python script with errors (for testing)

## Setup

1. Push this code to your GitHub repository
2. Set up AWS CodePipeline with:
   - Source: Your GitHub repository (dev branch)
   - Build: AWS CodeBuild using the included buildspec.yml

## Workflow

1. Push your Python code to the `dev` branch
2. CodePipeline will automatically:
   - Detect the push to dev
   - Check all Python files for errors
   - Use Claude 3.5 to fix any errors found
   - Commit the fixes back to the dev branch

This allows you to test and fix code in the dev branch before merging to main.
