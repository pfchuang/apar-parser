# APAR Parser

Parse IBM APAR (Authorized Program Analysis Report) information from IBM support pages.

## Installation

### Using uvx (Recommended)

**Note:** If you don't have uvx installed, see [Installing uv/uvx](#installing-uvuvx) below.

```bash
# Run directly
uvx apar-parser -i apar_list.txt -o output_dir

# Or run from local directory
uvx --from . apar-parser -i apar_list.txt -o output_dir
```

### Using pip

```bash
# Install from PyPI
pip install apar-parser

# Or install from local directory
pip install .
```

## Usage

### Process APAR list from file
```bash
apar-parser -i apar_list.txt -o output_dir
```

### Process single APAR
```bash
apar-parser -a OA41368 -o output_dir
```

### Output formats

**Text format (default):**
```bash
apar-parser -i apar_list.txt -o output_dir
```

**JSON format (structured data):**
```bash
apar-parser -i apar_list.txt -o output_dir -f json
```

### GUI mode (Windows only, requires tkinter)
```bash
apar-parser --gui
```

## Input File Format

Plain text file with one APAR number per line:
```
OA41368
OA36415
OA12345
```

## Output

### Text format
Creates text files in the output directory:
- `{APAR}.txt` - Successfully parsed APAR
- `{APAR}.notfound.txt` - APAR not found
- `{APAR}.logon.txt` - Requires IBM ID login

### JSON format
Creates JSON files with structured data:
```json
{
  "apar_number": "OA41368",
  "title": "ABEND0C4-11 IN EDGFLTS...",
  "modified_date": "21 May 2013",
  "apar_information": {
    "apar_number": "OA41368",
    "reported_component_name": "DFSMSRMM",
    ...
  },
  "problem_summary": "...",
  "problem_conclusion": "..."
}
```

## Options

- `-i, --input`: Input file with APAR numbers (one per line)
- `-o, --output`: Output directory (required unless using --gui)
- `-a, --apar`: Single APAR number to process
- `-f, --format`: Output format: `txt` or `json` (default: txt)
- `--gui`: Use GUI for file selection (Windows only, requires tkinter)

---

## Installing uv/uvx

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Or with pip:
```bash
pip install uv
```

## Disclaimer

This is an unofficial tool and is not affiliated with or endorsed by IBM. This tool parses publicly available APAR information from IBM support pages for convenience purposes only. Users are responsible for complying with IBM's terms of service and acceptable use policies when using this tool.

## Acknowledgments

Special thanks to *Tom Tsai*, the original author of this function.


