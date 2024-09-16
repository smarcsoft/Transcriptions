#!/bin/bash

# Function to install dependencies
install_dependencies() {
    local project_dir=$1
    local package_name=$2

    if [[ $package_name == "transcribe" ]] || [[ $package_name == "all" ]]; then
        pkg_name="transcribe"
        echo "Installing dependencies in $project_dir/package/$pkg_name..."
        pip install --target $project_dir/package/$pkg_name boto3 > /dev/null 2>&1
        pip install --target $project_dir/package/$pkg_name assemblyai > /dev/null 2>&1
        pip install --target $project_dir/package/$pkg_name mypy_boto3_s3 > /dev/null 2>&1
    fi
    if [[ $package_name == "summarize" ]] || [[ $package_name == "all" ]]; then
        pkg_name="summarize"
        echo "Installing dependencies in $project_dir/package/$pkg_name..."
        pip install --target $project_dir/package/$pkg_name boto3 > /dev/null 2>&1
        pip install --target $project_dir/package/$pkg_name openai > /dev/null 2>&1
        pip install --target $project_dir/package/$pkg_name mypy_boto3_s3 > /dev/null 2>&1
    fi
}


setup() {
    sync
    script_path="$(realpath "$0")"
    # Extract the directory path
    script_dir="$(dirname "$script_path")"
    # Get the parent directory
    parent_dir="$(dirname "$script_dir")"
}


cleanup() {
    local package_name=$1
    echo "Cleaning up old build files in $parent_dir/package/$package_name"
    rm -rf $parent_dir/package/$package_name
}

create_package() {
    local pkg_name=$1
    local current_dir=$(pwd)
    echo "Creating package $pkg_name..."
    mkdir -p $parent_dir/package/$package_name
    cd "$parent_dir/package/$pkg_name" || { echo "Failed to change to package directory" >&2; exit 1; }
    zip -r $parent_dir/$pkg_name.zip . > /dev/null 2>&1
    cd $parent_dir || { echo "Failed to change to parent directory" >&2; exit 1; }
    echo "Adding lambda function "$pkg_name"_lambda.py to package $parent_dir/$pkg_name.zip..."
    zip $parent_dir/$pkg_name.zip "$pkg_name"_lambda.py > /dev/null 2>&1 || { echo "Failed to add lambda function "$pkg_name"_lambda.py to package "$parent_dir"/"$pkg_name".zip" >&2; exit 1; }
    echo "Adding lambda function "$pkg_name".py..."
    zip $parent_dir/$pkg_name.zip "$pkg_name".py > /dev/null 2>&1 || { echo "Failed to add "$pkg_name".py to package "$parent_dir"/"$pkg_name".zip" >&2; exit 1; }
    echo "Adding config.py..."
    zip $parent_dir/$pkg_name.zip config.py > /dev/null 2>&1 || { echo "Failed to add config.py to package "$parent_dir"/"$pkg_name".zip" >&2; exit 1; }
    echo "Removing pycache files from package $parent_dir/$pkg_name.zip..."
    zip -d $parent_dir/$pkg_name.zip "*/__pycache__/*" > /dev/null 2>&1 || { echo "Failed to remove pycache files from package $parent_dir/$pkg_name.zip" >&2; exit 1; }
    # move the zip file to the package directory
    mv $parent_dir/$pkg_name.zip $parent_dir/package
    echo "Package available at package/$pkg_name.zip !"
}


# Process argument
if [[ $1 == "--package" ]]; then
    package_name=$2
else
    echo "Invalid argument. Usage: $0 --package <package_name>|all"
    echo "package_name can either be transcribe or summarize"
    exit 1
fi

# Check if package_name is either "transcription" or "summarization"
if [[ $package_name != "transcribe" && $package_name != "summarize" && $package_name != "all" ]]; then
    echo "Invalid package_name. Allowed values are 'transcribe' or 'summarize' or 'all'. Value give is $package_name"
    exit 1
fi


setup
if [[ $package_name != "all" ]]; then
    # Call the function to install dependencies
    install_dependencies $parent_dir $package_name
    # Call the function to create the package
    create_package $package_name
    if [[ $package_name == "transcribe" ]]; then
        $script_dir/upload_lambda.sh Transcription $parent_dir/package/transcribe.zip eu-west-1
    fi
    if [[ $package_name == "summarize" ]]; then
        $script_dir/upload_lambda.sh Summarization $parent_dir/package/summarize.zip eu-west-1
    fi
    cleanup $package_name
else
    # Call the function to install dependencies
    install_dependencies $parent_dir "transcribe"
    # Call the function to create all packages
    create_package "transcribe"
    cleanup "transcribe"
    install_dependencies $parent_dir "summarize"
    create_package "summarize"
    $script_dir/upload_lambda.sh Transcription $parent_dir/package/transcribe.zip eu-west-1
    $script_dir/upload_lambda.sh Summarization $parent_dir/package/summarize.zip eu-west-1
    cleanup "summarize"
fi
