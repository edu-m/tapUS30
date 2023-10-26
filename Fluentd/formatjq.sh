#!/bin/bash

# Define the source directory where your JSON files are located
source_directory="raw/"

# Create the "formatted" directory if it doesn't exist
# mkdir -p "$source_directory/formatted"

# Iterate through JSON files in the source directory
for file in "$source_directory"*.json; do
    if [ -e "$file" ]; then
        # Process the JSON file with jq and save it in the "formatted" folder
        filename=$(basename "$file")
        jq . "$file" > "formatted/$filename"
        echo "Processed: $filename"
    fi
done

echo "Processing complete. Formatted files are in 'formatted/'."
