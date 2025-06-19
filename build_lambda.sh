#!/bin/bash

# Build script for Lambda function
echo "Building Lambda function..."

# Create a temporary directory for the build
BUILD_DIR="lambda_build"
rm -rf $BUILD_DIR
mkdir -p $BUILD_DIR

# Copy the Lambda function from lambda/ directory
cp lambda/lambda_function.py $BUILD_DIR/

# Install dependencies (if you have any)
# pip install -r lambda/requirements.txt -t $BUILD_DIR/

# Create the ZIP file
cd $BUILD_DIR
zip -r ../lambda_function.zip .
cd ..

# Clean up
rm -rf $BUILD_DIR

echo "Lambda function packaged as lambda_function.zip" 