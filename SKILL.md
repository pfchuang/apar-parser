# APAR Parser Skill

## Description

Parse IBM APAR (Authorized Program Analysis Report) information from IBM support pages and save to text or JSON format.

## Capabilities

- Fetch APAR information from IBM support website
- Parse APAR details including status, problem summary, fix information, etc.
- Support batch processing from input file
- Output in text format (with section separators) or structured JSON
- Handle special cases (login required, not found)

## Usage

### Parse single APAR
```bash
apar-parser -a <APAR_NUMBER> -o <OUTPUT_DIR>
```

### Parse multiple APARs from file
```bash
apar-parser -i <INPUT_FILE> -o <OUTPUT_DIR>
```

### Output as JSON
```bash
apar-parser -a <APAR_NUMBER> -o <OUTPUT_DIR> -f json
```

## Input Format

For batch processing, create a text file with one APAR number per line:
```
OA41368
OA36415
OA12345
```

## Output

### Text Format
Creates `{APAR}.txt` files with sections separated by `--`:
- APAR status
- Error description
- Problem summary
- Problem conclusion
- APAR Information (metadata)
- Fix information
- Applicable component levels

### JSON Format
Creates `{APAR}.json` files with structured data containing all fields as key-value pairs.

### Special Cases
- `{APAR}.notfound.txt` - APAR does not exist
- `{APAR}.logon.txt` - Requires IBM ID authentication

## Installation

```bash
# Using uvx (recommended)
uvx apar-parser -a OA41368 -o output

# Using pip
pip install apar-parser
```

## When to Use This Skill

- User needs to fetch IBM APAR information
- User wants to analyze multiple APARs
- User needs structured APAR data for further processing
- User is researching IBM system issues or fixes

## Example Scenarios

**Scenario 1: Single APAR lookup**
```
User: "Get information for APAR OA41368"
Agent: apar-parser -a OA41368 -o ./apar_data
```

**Scenario 2: Batch processing**
```
User: "Parse all APARs in this list"
Agent: apar-parser -i apar_list.txt -o ./apar_results
```

**Scenario 3: JSON output for analysis**
```
User: "Get APAR data in JSON format for analysis"
Agent: apar-parser -a OA41368 -o ./data -f json
```

## Notes

- Requires internet connection to fetch from IBM support website
- Some APARs may require IBM ID login (will be saved as .logon.txt)
- APAR numbers are typically 7 characters (e.g., OA41368)
