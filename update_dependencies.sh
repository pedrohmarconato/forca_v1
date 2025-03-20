#!/bin/bash

# Script to update dependency summaries
echo "Updating dependency summaries..."

# Create node_modules summary
echo "Number of modules: $(find /home/pmarconato/APP_FORCA/FORCA_V1/frontend/node_modules -type d -maxdepth 1 | wc -l)" > node_modules_summary.txt
echo "First 20 modules:" >> node_modules_summary.txt
find /home/pmarconato/APP_FORCA/FORCA_V1/frontend/node_modules -type d -maxdepth 1 | sort | head -n 20 >> node_modules_summary.txt

# Create package.json dependencies summary
echo "Dependencies list:" > package_dependencies.txt
grep -o '"[^"]*": "[^"]*"' /home/pmarconato/APP_FORCA/FORCA_V1/frontend/package.json | grep -A 999 "@testing" | grep -B 999 "web-vitals" >> package_dependencies.txt

echo "Summary files updated successfully!"