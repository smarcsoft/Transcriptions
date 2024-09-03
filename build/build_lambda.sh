#!/bin/bash

echo "Cleaning up old build files"
# Get the absolute path of the script
script_path="$(realpath "$0")" || { echo "Failed to determine script path" >&2; exit 1; }
# Extract the directory path
script_dir="$(dirname "$script_path")"
# Get the parent directory
parent_dir="$(dirname "$script_dir")"
echo "Cleaning up: $parent_dir/package"
rm -rf $parent_dir/transcriptions.zip
rm -rf $parent_dir/package
mkdir $parent_dir/package
echo "Installing dependencies"
pip install --target $parent_dir/package boto3
pip install --target $parent_dir/package assemblyai
pip install --target $parent_dir/package mypy_boto3_s3
echo "Creating package..."
current_dir=$(pwd)
cd "$parent_dir/package" || { echo "Failed to change to package directory" >&2; exit 1; }
zip -r $parent_dir/transcriptions.zip .
cd $parent_dir || { echo "Failed to change to parent directory" >&2; exit 1; }
zip $parent_dir/transcriptions.zip transcribe_lambda.py
zip -d $parent_dir/transcriptions.zip "*/__pycache__/*"
echo "Package done!"