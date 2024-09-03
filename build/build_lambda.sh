#!/bin/bash

echo "Cleaning up old build files"
parent_dir=$(dirname "$(readlink -f "$0")")
rm -rf $parent_dir/transcriptions.zip
rm -rf $parent_dir/package
mkdir $parent_dir/package
echo "Installing dependencies"
pip install --target $parent_dir/package boto3
pip install --target $parent_dir/package assemblyai
echo "Creating package..."
current_dir=$(pwd)
cd $parent_dir/package
zip -r $parent_dir/transcriptions.zip .
cd $parent_dir
zip $parent_dir/transcriptions.zip transcribe_lambda.py
zip -d $parent_dir/transcriptions.zip "*/__pycache__/*"
cd $current_dir
echo "Package done!"