# sancov2lcov

A simple Python tool to convert LLVM's `sancov` JSON coverage reports (produced by `--symcov`) into LCOV `.info` format.

This is useful for visualizing coverage data from fuzzing campaigns or other sanitizers using standard LCOV tooling like `genhtml`.

## Installation

No installation is required. Just copy `sancov2lcov.py` and run it.

```bash
git clone https://github.com/your-username/sancov2lcov.git
cd sancov2lcov
chmod +x sancov2lcov.py
```

## Usage

### 1. Generate Sancov JSON Data

First, ensure you have a binary compiled with sanitizer coverage (e.g., `-fsanitize-coverage=trace-pc-guard,trace-cmp`). When run, this binary produces `.sancov` files.

Use the `sancov` tool (from LLVM) to symbolize and convert the raw coverage data into a JSON report. You might need to use a script like `cov.py` (often found in LLVM source trees) or just use `llvm-cov` if your setup supports it directly, but this tool specifically targets the JSON output format that looks like this:

```json
{
  "covered-points": ["0x1234", ...],
  "point-symbol-info": {
    "source_file.c": {
      "0x1234": "10:5"
    }
  }
}
```

### 2. Convert to LCOV

Run `sancov2lcov.py` to convert the JSON report into an LCOV `.info` file:

```bash
./sancov2lcov.py --symcov coverage.json --output coverage.info --srcpath /path/to/source/root
```

**Arguments:**

*   `--symcov`: Path to the input JSON file (required).
*   `--output`: Path to the output `.info` file (required).
*   `--srcpath`: Path to the source code root. This is used to resolve relative paths in the JSON report to absolute paths in the LCOV file. Default is `.` (current directory).

### 3. Generate HTML Report

Once you have the `coverage.info` file, use `genhtml` (part of the `lcov` package) to generate a browsable HTML report:

```bash
genhtml coverage.info -o html_report
```

You can then open `html_report/index.html` in your browser.

## Example

```bash
# Assuming you have a 'coverage.json' from your fuzzer run
./sancov2lcov.py --symcov coverage.json --output coverage.info --srcpath .

# Generate HTML report in 'out' directory
genhtml coverage.info -o out
```

## License

MIT License
