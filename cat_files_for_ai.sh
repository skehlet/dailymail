#!/bin/bash

# Set the output file
OUTPUT_FILE="project_code.txt"

# Clear the output file if it exists
> "$OUTPUT_FILE"

# Process files using process substitution to handle filenames with spaces better
while read -r file; do
    # Skip if file is too large (>1MB)
    if [[ $(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null) -gt 1048576 ]]; then
      echo "SKIPPING LARGE FILE: $file" >> "$OUTPUT_FILE"
      continue
    fi
    
    echo "============================================================" >> "$OUTPUT_FILE"
    echo "FILE: $file" >> "$OUTPUT_FILE"
    echo "============================================================" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
    
    # Use file command to check if it's binary
    if file "$file" | grep -q "text"; then
      cat "$file" >> "$OUTPUT_FILE"
    else
      echo "[BINARY FILE - CONTENTS NOT SHOWN]" >> "$OUTPUT_FILE"
    fi
    
    echo "" >> "$OUTPUT_FILE"
    echo "" >> "$OUTPUT_FILE"
done < <(find -P . -type f \
  -not -path "*/\.*" \
  -not -path "*/.git/*" \
  -not -path "*/.venv/*" \
  -not -path "*/venv/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*/node_modules/*" \
  -not -name ".DS_Store" \
  -not -name "*.pyc" \
  -not -name "*.bin" \
  -not -name "*.o" \
  -not -name "*.so" \
  -not -name "*.dylib" \
  -not -name "*.dll" \
  -not -name "*.exe" \
  -not -name "*.png" \
  -not -name "*.jpg" \
  -not -name "*.jpeg" \
  -not -name "*.gif" \
  -not -name "*.bmp" \
  -not -name "*.tiff" \
  -not -name "*.ico" \
  -not -name "*.svg" \
  -not -name "*.webp" \
  -not -name "project_code.txt" \
  2>/dev/null | sort)

echo "All files have been collected in $OUTPUT_FILE"
ls -lah "$OUTPUT_FILE"
