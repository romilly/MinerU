# MinerU API Function Testing Note

## Context
Created a Python API wrapper function for MinerU CLI functionality to allow programmatic access without using command-line interface.

## What Was Done
1. **Created `/home/romilly/git/forked/MinerU/mineru/api.py`** - Contains `parse_pdf()` function
2. **Function mimics CLI behavior** - Uses same defaults and core logic as `mineru` command
3. **Bypasses Click framework** - Directly calls core parsing functions to avoid CLI decorator issues

## API Function Details
- **File**: `mineru/api.py`
- **Function**: `parse_pdf(input_path, output_dir, **kwargs)`
- **Required params**: Only `input_path` and `output_dir`
- **Defaults**: Same as CLI (method='auto', backend='pipeline', lang='ch', etc.)

## Testing Status
- **Demo file exists**: `demo/pdfs/demo1.pdf` ✓
- **Function created**: ✓
- **Testing attempted**: ✗ (torch dependency issue on this machine)

## Next Steps for Testing
1. **Activate virtual environment**: `source .venv/bin/activate`
2. **Install dependencies if needed**: `pip install -e .[core]`
3. **Test the function**:
   ```python
   from mineru.api import parse_pdf
   parse_pdf('demo/pdfs/demo1.pdf', '/tmp/test_output')
   ```

## Expected Behavior
- Should create markdown files in output directory
- Should generate same output as: `mineru -p demo/pdfs/demo1.pdf -o /tmp/test_output`

## Usage Example
```python
from mineru.api import parse_pdf

# Basic usage (uses all defaults)
parse_pdf('document.pdf', 'output/')

# With custom settings
parse_pdf('document.pdf', 'output/', backend='vlm-transformers', lang='en')
```

## Issues Encountered
- `torch` import error when calling `get_device()` function
- Virtual environment on writing machine may not have full dependencies installed
- Function should work once proper environment is activated on target machine