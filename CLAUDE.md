# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

MinerU is a practical tool for converting PDF documents to Markdown format. It's a sophisticated document processing pipeline that supports multiple backends (pipeline-based and VLM-based) for different use cases.

## Core Architecture

- **Backend Systems**: Two main processing backends
  - `pipeline`: Traditional computer vision pipeline with separate models for layout detection, OCR, formula recognition, and table parsing
  - `vlm`: Vision-Language Model (MinerU2.5) for end-to-end document understanding
- **CLI Interface**: Primary entry point via `mineru` command with support for batch processing
- **Model Components**: Modular design with separate models for:
  - Layout detection (`mineru/model/layout/`)
  - OCR (`mineru/model/ocr/`)
  - Mathematical formula recognition (`mineru/model/mfr/`)
  - Table recognition (`mineru/model/table/`)
  - Reading order determination (`mineru/model/reading_order/`)
- **Data Pipeline**: Abstracted I/O layer supporting local files and S3 storage (`mineru/data/`)

## Essential Commands

### Installation and Setup
```bash
# Install with core dependencies
pip install -e .[core]

# Install with all optional dependencies
pip install -e .[all]

# Download models (required for pipeline backend)
mineru-models-download

# Check available CLI options
mineru --help
```

### Development and Testing
```bash
# Run tests with coverage
pytest -s --cov=mineru --cov-report html

# Run specific test suite
python -m pytest tests/unittest/test_e2e.py

# Build package
python -m build --wheel

# Install in development mode
pip install -e .[test]
```

### Main Usage Patterns
```bash
# Basic PDF conversion
mineru -p input.pdf -o output_dir

# Batch processing directory
mineru -p /path/to/pdfs/ -o /output/dir/

# Force specific backend
mineru -p input.pdf -o output_dir --backend vlm
mineru -p input.pdf -o output_dir --backend pipeline

# Specify parsing method (pipeline backend only)
mineru -p input.pdf -o output_dir --method ocr
```

### Server Components
```bash
# Start API server
mineru-api

# Start Gradio web interface
mineru-gradio

# Start vLLM inference server (for VLM backend)
mineru-vllm-server
```

## Key Configuration

- **Model Downloads**: Models are automatically downloaded to `~/.cache/mineru/` on first use
- **Backend Selection**: Controlled via `--backend` flag (auto-detects based on model availability)
- **Output Format**: Generates markdown files plus intermediate JSON files (`middle.json`, `content_list.json`)
- **Supported Formats**: PDF, PNG, JPG, JPEG input files

## Project Structure Notes

- Entry points defined in `pyproject.toml` under `[project.scripts]`
- CLI parsing logic in `mineru/cli/client.py`
- Core parsing logic split between `mineru/backend/pipeline/` and `mineru/backend/vlm/`
- Version management in `mineru/version.py`
- Model configuration and initialization in `mineru/backend/pipeline/model_init.py`

## Important Development Notes

- The project uses setuptools with dynamic versioning
- Test configuration in `pyproject.toml` with coverage reporting
- VLM backend requires significant GPU memory (model is 1.2B parameters)
- Pipeline backend can run on CPU but GPU acceleration recommended
- Docker deployment supported via `docker/compose.yaml`