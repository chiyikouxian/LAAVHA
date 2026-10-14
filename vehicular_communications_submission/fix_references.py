#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix reference format
"""

import re
import sys

# Set UTF-8 output for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

def fix_reference_format(content):
    """Fix reference format"""
    # Pattern: {\bf year}, {\em volume},
    # Replace: year, volume,
    pattern = r'\{\\bf (\d{4})\}, \{\\em (\d+)\},'
    replacement = r'\1, \2,'

    fixed_content = re.sub(pattern, replacement, content)

    # Count changes
    matches = re.findall(pattern, content)
    print(f"Found {len(matches)} patterns to fix")

    return fixed_content

def main():
    input_file = 'main.tex'
    output_file = 'main.tex'

    # Read file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix format
    fixed_content = fix_reference_format(content)

    # Write back
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(fixed_content)

    print(f"Done! File saved to {output_file}")

if __name__ == '__main__':
    main()
