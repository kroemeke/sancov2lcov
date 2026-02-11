#!/usr/bin/env python3
import argparse
import json
import os
import sys

def main():
    parser = argparse.ArgumentParser(description="Convert sancov JSON to LCOV info format")
    parser.add_argument("--sancov", required=True, help="Input sancov JSON file")
    parser.add_argument("--output", required=True, help="Output LCOV info file")
    parser.add_argument("--srcpath", default=".", help="Root source directory to resolve relative paths")
    args = parser.parse_args()

    try:
        with open(args.sancov, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error loading sancov file: {e}", file=sys.stderr)
        sys.exit(1)

    covered_points = set(data.get("covered-points", []))
    point_symbol_info = data.get("point-symbol-info", {})

    print(f"Found {len(covered_points)} covered points.")
    print(f"Processing {len(point_symbol_info)} files...")

    with open(args.output, 'w') as out:
        for filename, functions in point_symbol_info.items():
            # Resolve absolute path
            # If filename is already absolute, join ignores srcpath. 
            # If relative, it joins.
            # Note: os.path.join("/abs/path", "rel/path") -> "/abs/path/rel/path"
            # os.path.join("/abs/path", "/other/abs") -> "/other/abs"
            
            full_path = os.path.join(args.srcpath, filename)
            full_path = os.path.abspath(full_path)

            out.write(f"TN:\n")
            out.write(f"SF:{full_path}\n")

            # Dictionary to map line_number -> execution_count
            line_coverage = {} 
            all_lines = set()

            # Iterate over all functions and their points
            for func_name, points in functions.items():
                for point_id, loc in points.items():
                    try:
                        # Location format is usually "line:column" or just "line"
                        line_str = loc.split(':')[0]
                        line = int(line_str)
                        if line <= 0:
                            continue
                    except ValueError:
                        continue
                    
                    all_lines.add(line)
                    
                    is_covered = point_id in covered_points
                    
                    # Initialize line in map if not present
                    if line not in line_coverage:
                        line_coverage[line] = 0
                        
                    if is_covered:
                        line_coverage[line] += 1

            # Write DA records sorted by line number
            # DA:<line number>,<execution count>
            for line in sorted(all_lines):
                count = line_coverage.get(line, 0)
                out.write(f"DA:{line},{count}\n")

            # Summary for the file
            out.write(f"LF:{len(all_lines)}\n")
            lines_hit = sum(1 for c in line_coverage.values() if c > 0)
            out.write(f"LH:{lines_hit}\n")
            out.write("end_of_record\n")

    print(f"Successfully converted coverage data to {args.output}")

if __name__ == "__main__":
    main()
