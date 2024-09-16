#!/bin/bash
# Script to update an AWS Lambda function code from a zip package
# Usage: ./upload_lambda_code.sh <function_name> <zip_file_path> [region]

# Check if at least two arguments are provided
if [ $# -lt 2 ]; then
    echo "Usage: $0 <function_name> <zip_file_path> [region]"
    exit 1
fi

FUNCTION_NAME=$1
ZIP_FILE_PATH=$2
REGION=${3:-us-east-1}  # Default region is us-east-1 if not specified

# Check if the zip file exists
if [ ! -f "$ZIP_FILE_PATH" ]; then
    echo "Error: Zip file '$ZIP_FILE_PATH' not found."
    exit 1
fi

echo "Uploading $ZIP_FILE_PATH to function $FUNCTION_NAME..."

# Update the Lambda function code
aws lambda update-function-code \
    --function-name "$FUNCTION_NAME" \
    --zip-file "fileb://$ZIP_FILE_PATH" \
    --region "$REGION" \
    --no-cli-pager > /dev/null 2>&1

# Check if the update was successful
if [ $? -eq 0 ]; then
    echo "Successfully updated Lambda function '$FUNCTION_NAME'."
else
    echo "Failed to update Lambda function '$FUNCTION_NAME'."
    exit 1
fi
