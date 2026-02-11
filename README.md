# sancov2lcov & lcov2llm

A toolkit for converting LLVM sanitizer coverage into formats usable by humans (`genhtml`) and LLM agents (`lcov2llm`).

## Tools Included

1.  **`sancov2lcov`**: Converts raw `sancov` JSON data into LCOV `.info` format.
2.  **`lcov2llm`**: Analyzes the LCOV data to produce a "Frontier Report" — identifying exactly where execution stopped (Hit -> Miss transitions). This is designed to help LLM agents understand coverage gaps without reading the entire codebase.

## 1. Installation

No installation required. Clone and run:

```bash
git clone https://github.com/your-username/sancov2lcov.git
cd sancov2lcov
chmod +x sancov2lcov lcov2llm
```

## 2. Generating Coverage Data

First, run your sanitized binary to generate `.sancov` files:

```bash
# Enable coverage generation
export ASAN_OPTIONS=coverage=1 

# Run your fuzzer/binary
./nginx_fuzzer
```

This produces files like `nginx_fuzzer.12345.sancov`.

Next, convert these to a JSON report using LLVM's `sancov` tool:

```bash
sancov -symbolize ./nginx_fuzzer *.sancov > coverage.json
```

## 3. Converting to LCOV

Convert the JSON report to the standard LCOV `.info` format:

```bash
./sancov2lcov --symcov coverage.json --output coverage.info --srcpath /path/to/source
```

## 4. Human Analysis (HTML Report)

Use standard tools to view the coverage:

```bash
genhtml coverage.info -o html_report
# Open html_report/index.html in browser
```

## 5. LLM Agent Analysis (Frontier Report)

Use `lcov2llm` to generate a text-based report for AI analysis. This tool finds the "edges" of coverage—where your fuzzer hit a line but failed to execute the next logical block (usually a failed `if` check).

```bash
./lcov2llm coverage.info --srcpath /path/to/source > analysis_report.md
```

### Example Output

The report highlights the **Frontier** (Hit -> Miss) and provides context (including function headers), making it easy to spot why code wasn't reached.

```c
# Coverage Frontier Report

## File: `/home/user/src/core/nginx.c`
Found 35 frontiers.

### Frontier at line 198 -> 208
```c
 196 |       int ngx_cdecl
 197 |       main(int argc, char *const *argv)
 198 | HIT > {
 199 |           ngx_buf_t        *b;
 200 |           ngx_log_t        *log;
 ...
 206 |           ngx_debug_init();
 207 |       
 208 | MISS|     if (ngx_strerror_init() != NGX_OK) {
 209 |               return 1;
 210 |           }
```

In this example, the agent can clearly see that `main` was entered (Line 198), but the error handling block at Line 208 was never taken (because `ngx_strerror_init` succeeded).

## License

MIT License
