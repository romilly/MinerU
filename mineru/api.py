"""
Python API wrapper for MinerU CLI functionality.

This module provides a simple Python function interface to MinerU's PDF parsing
capabilities, using the same underlying logic as the CLI but with sensible defaults.
"""

import os
from pathlib import Path
from typing import Optional, Union

# Import the core functions directly
from mineru.cli.common import do_parse, read_fn, pdf_suffixes, image_suffixes
from mineru.utils.config_reader import get_device
from mineru.utils.guess_suffix_or_lang import guess_suffix_by_path
from mineru.utils.model_utils import get_vram


def parse_pdf(
    input_path: Union[str, Path],
    output_dir: Union[str, Path],
    method: str = 'auto',
    backend: str = 'pipeline',
    lang: str = 'ch',
    server_url: Optional[str] = None,
    start_page_id: int = 0,
    end_page_id: Optional[int] = None,
    formula_enable: bool = True,
    table_enable: bool = True,
    device_mode: Optional[str] = None,
    virtual_vram: Optional[int] = None,
    model_source: str = 'huggingface',
    **kwargs
) -> None:
    """
    Parse PDF documents to Markdown using MinerU.

    This function provides a Python API interface to MinerU's CLI functionality,
    using the same defaults as the command-line interface.

    Args:
        input_path: Path to input PDF file or directory containing PDFs/images
        output_dir: Output directory for generated markdown files
        method: Parsing method ('auto', 'txt', 'ocr'). Default: 'auto'
        backend: Processing backend ('pipeline', 'vlm-transformers', 'vlm-vllm-engine', 'vlm-http-client'). Default: 'pipeline'
        lang: Language for OCR accuracy ('ch', 'en', 'korean', etc.). Default: 'ch'
        server_url: Server URL when using 'vlm-http-client' backend. Default: None
        start_page_id: Starting page for PDF parsing (0-indexed). Default: 0
        end_page_id: Ending page for PDF parsing (0-indexed). Default: None (all pages)
        formula_enable: Enable formula parsing. Default: True
        table_enable: Enable table parsing. Default: True
        device_mode: Device for model inference ('cpu', 'cuda', 'cuda:0', etc.). Default: None (auto-detect)
        virtual_vram: GPU memory limit in MB. Default: None (auto-detect)
        model_source: Model repository source ('huggingface', 'modelscope', 'local'). Default: 'huggingface'
        **kwargs: Additional arguments passed to the underlying parser

    Raises:
        FileNotFoundError: If input_path doesn't exist
        ValueError: If invalid arguments are provided

    Example:
        >>> from mineru.api import parse_pdf
        >>> parse_pdf('document.pdf', 'output/')
        >>> parse_pdf('/path/to/pdfs/', 'output/', backend='vlm-transformers')
    """
    # Convert paths to strings for compatibility with CLI function
    input_path = str(input_path)
    output_dir = str(output_dir)

    # Validate input path exists
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Input path does not exist: {input_path}")

    # Validate method choices
    valid_methods = ['auto', 'txt', 'ocr']
    if method not in valid_methods:
        raise ValueError(f"Invalid method '{method}'. Must be one of: {valid_methods}")

    # Validate backend choices
    valid_backends = ['pipeline', 'vlm-transformers', 'vlm-vllm-engine', 'vlm-http-client']
    if backend not in valid_backends:
        raise ValueError(f"Invalid backend '{backend}'. Must be one of: {valid_backends}")

    # Validate language choices
    valid_langs = ['ch', 'ch_server', 'ch_lite', 'en', 'korean', 'japan', 'chinese_cht',
                   'ta', 'te', 'ka', 'th', 'el', 'latin', 'arabic', 'east_slavic',
                   'cyrillic', 'devanagari']
    if lang not in valid_langs:
        raise ValueError(f"Invalid language '{lang}'. Must be one of: {valid_langs}")

    # Validate model source choices
    valid_sources = ['huggingface', 'modelscope', 'local']
    if model_source not in valid_sources:
        raise ValueError(f"Invalid model_source '{model_source}'. Must be one of: {valid_sources}")

    # Set up environment variables (from cli/client.py logic)
    if not backend.endswith('-client'):
        def get_device_mode() -> str:
            if device_mode is not None:
                return device_mode
            else:
                return get_device()

        if os.getenv('MINERU_DEVICE_MODE', None) is None:
            os.environ['MINERU_DEVICE_MODE'] = get_device_mode()

        def get_virtual_vram_size() -> int:
            if virtual_vram is not None:
                return virtual_vram
            if get_device_mode().startswith("cuda") or get_device_mode().startswith("npu"):
                return round(get_vram(get_device_mode()))
            return 1

        if os.getenv('MINERU_VIRTUAL_VRAM_SIZE', None) is None:
            os.environ['MINERU_VIRTUAL_VRAM_SIZE'] = str(get_virtual_vram_size())

        if os.getenv('MINERU_MODEL_SOURCE', None) is None:
            os.environ['MINERU_MODEL_SOURCE'] = model_source

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Core parsing function (from cli/client.py logic)
    def parse_doc(path_list: list[Path]):
        try:
            file_name_list = []
            pdf_bytes_list = []
            lang_list = []
            for path in path_list:
                file_name = str(Path(path).stem)
                pdf_bytes = read_fn(path)
                file_name_list.append(file_name)
                pdf_bytes_list.append(pdf_bytes)
                lang_list.append(lang)

            do_parse(
                output_dir=output_dir,
                pdf_file_names=file_name_list,
                pdf_bytes_list=pdf_bytes_list,
                p_lang_list=lang_list,
                backend=backend,
                parse_method=method,
                formula_enable=formula_enable,
                table_enable=table_enable,
                server_url=server_url,
                start_page_id=start_page_id,
                end_page_id=end_page_id,
                **kwargs,
            )
        except Exception as e:
            raise e

    # Handle single file or directory input
    if os.path.isdir(input_path):
        doc_path_list = []
        for doc_path in Path(input_path).glob('*'):
            if guess_suffix_by_path(doc_path) in pdf_suffixes + image_suffixes:
                doc_path_list.append(doc_path)
        parse_doc(doc_path_list)
    else:
        parse_doc([Path(input_path)])