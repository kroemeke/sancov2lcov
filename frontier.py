#!/usr/bin/env python3
import argparse
import os
import sys
import re

def parse_info(info_path):
    files = {}
    current_file = None
    try:
        with open(info_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('SF:'):
                    current_file = line[3:]
                    files[current_file] = {}
                elif line.startswith('DA:'):
                    if current_file:
                        parts = line[3:].split(',')
                        ln = int(parts[0])
                        count = int(parts[1])
                        files[current_file][ln] = count
    except Exception as e:
        print(f"Error parsing info file: {e}", file=sys.stderr)
        sys.exit(1)
    return files

def find_function_header(all_lines, center_line, limit=100):
    """
    Scan backwards from center_line to find a likely function header.
    Heuristic: Look for a line starting with non-whitespace (column 0)
    that isn't a preprocessor directive (#) or a brace (}).
    """
    idx = center_line - 1
    found_lines = []
    
    start_idx = -1
    
    for i in range(idx, max(-1, idx - limit), -1):
        if i >= len(all_lines): continue
        line = all_lines[i]
        
        # Skip empty lines
        if not line.strip():
            continue

        # If we hit a closing brace at start of line, we likely left the function
        if line.startswith('}'):
            break
            
        # If we see a line starting with non-whitespace (and not #), it's a candidate
        if line and line[0].strip() and not line.startswith('#'):
            start_idx = i
            break
            
    if start_idx != -1:
        # Include a few lines around the found header
        end_header = min(start_idx + 2, center_line - 1)
        for i in range(start_idx, end_header + 1):
             if i < len(all_lines):
                 found_lines.append((i+1, all_lines[i].rstrip()))
                 
    return found_lines

def get_context(filepath, center_line, lookahead_line, context_lines=15):
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            all_lines = f.readlines()
    except Exception as e:
        return [f"Error reading file: {e}"]
    
    # Determine range to show
    start = max(1, center_line - context_lines)
    # Ensure we cover the missed line
    end = max(lookahead_line, center_line + context_lines)
    end = min(len(all_lines), end)
    
    # Cap huge gaps (e.g. if jump is > 20 lines)
    if lookahead_line - center_line > 20:
        end = min(len(all_lines), center_line + context_lines)

    result = []
    
    # 1. Try to find function header if it's not in the immediate range
    if start > 5:
        header_lines = find_function_header(all_lines, start)
        if header_lines:
            for ln, content in header_lines:
                result.append(f"{ln:4d} | {content}")
            result.append(" ... ")

    # 2. Show the main context
    for i in range(start, end + 1):
        idx = i - 1
        if idx < len(all_lines):
            prefix = "      "
            # Highlight the 'frontier' edge
            if i == center_line:
                prefix = "HIT > "
            elif i == lookahead_line:
                prefix = "MISS| "
            
            line_content = all_lines[idx].rstrip()
            result.append(f"{i:4d} | {prefix}{line_content}")
            
    return result

def main():
    parser = argparse.ArgumentParser(description="Find coverage frontiers (Hit -> Miss transitions)")
    parser.add_argument("info_file", help="Path to coverage.info file")
    parser.add_argument("--srcpath", default=".", help="Root source directory (optional, if SF paths are relative)")
    parser.add_argument("--context", type=int, default=15, help="Number of context lines to show (default: 15)")
    args = parser.parse_args()

    files = parse_info(args.info_file)
    
    print(f"# Coverage Frontier Report\n")
    
    total_frontiers = 0
    
    # Sort files for deterministic output
    for filepath in sorted(files.keys()):
        lines = files[filepath]
        sorted_lines = sorted(lines.keys())
        file_frontiers = []
        
        for i in range(len(sorted_lines) - 1):
            l1 = sorted_lines[i]
            l2 = sorted_lines[i+1]
            
            c1 = lines[l1]
            c2 = lines[l2]
            
            # Check for Frontier: Hit followed by Miss
            if c1 > 0 and c2 == 0:
                file_frontiers.append((l1, l2))

        if file_frontiers:
            # Resolve path if needed
            real_path = filepath
            if not os.path.exists(real_path) and args.srcpath:
                 joined = os.path.join(args.srcpath, filepath)
                 if os.path.exists(joined):
                     real_path = joined

            print(f"## File: `{filepath}`")
            print(f"Found {len(file_frontiers)} frontiers.\n")
            
            for hit_line, miss_line in file_frontiers:
                total_frontiers += 1
                print(f"### Frontier at line {hit_line} -> {miss_line}")
                print("```c")
                context = get_context(real_path, hit_line, miss_line, args.context)
                for line in context:
                    print(line)
                print("```\n")

    print(f"\nTotal Frontiers Found: {total_frontiers}")

if __name__ == "__main__":
    main()
