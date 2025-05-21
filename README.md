# Python Error Fixer with AWS CodePipeline and Claude

Automatically fixes Python errors in your code using AWS CodePipeline and Claude 3.5 (AWS Bedrock).

## Files

- `fix_python_errors.py`: Script that uses Claude 3.5 to detect and fix Python errors
- `buildspec.yml`: AWS CodeBuild configuration
- `broken_script.py`: Sample Python script with errors (for testing)

## Setup

1. Push this code to your GitHub repository
2. Set up AWS CodePipeline with:
   - Source: Your GitHub repository
   - Build: AWS CodeBuild using the included buildspec.yml

The pipeline will automatically fix any Python errors in your code using Claude 3.5 when you push changes.
