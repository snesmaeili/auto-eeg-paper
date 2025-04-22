import os
import yaml
import json
import base64
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def save_image(img_data: str, output_dir: Path, notebook_name: str, cell_index: int) -> str:
    """Save a base64 encoded image to disk.
    
    Args:
        img_data: Base64 encoded image data
        output_dir: Directory to save the image
        notebook_name: Name of the notebook (used for subdirectory)
        cell_index: Cell index (used for file naming)
        
    Returns:
        Path to the saved image
    """
    try:
        # Create directory for notebook images
        img_dir = output_dir / "figures" / notebook_name.replace(".ipynb", "")
        img_dir.mkdir(parents=True, exist_ok=True)
        
        # Save the image
        img_path = img_dir / f"cell_{cell_index}.png"
        img_path.write_bytes(base64.b64decode(img_data))
        
        return str(img_path)
    except Exception as e:
        logger.error(f"Failed to save image for {notebook_name}, cell {cell_index}: {str(e)}")
        return ""


def process_notebook_outputs(
    summary: Dict[str, List[Dict[str, Any]]],
    output_dir: Path
) -> Dict[str, List[Dict[str, Any]]]:
    """Process notebook outputs, saving images and organizing data.
    
    Args:
        summary: Dictionary of notebook outputs from YAML
        output_dir: Directory to save images and other outputs
        
    Returns:
        Processed data ready for JSON serialization
    """
    aggregated = {"notebooks": []}
    
    for nb_name, cells in summary.items():
        logger.info(f"Processing notebook: {nb_name}")
        nb_entry = {"name": nb_name, "cells": []}
        
        for cell in cells:
            entry = {"cell_index": cell["cell_index"], "outputs": []}
            
            for out in cell.get("outputs", []):
                output_type = out.get("type")
                
                if output_type == "text":
                    entry["outputs"].append({"type": "text", "text": out["text"]})
                    
                elif output_type == "image":
                    img_path = save_image(
                        out["data"], 
                        output_dir, 
                        nb_name, 
                        cell["cell_index"]
                    )
                    if img_path:
                        entry["outputs"].append({"type": "image", "path": img_path})
                        
                else:
                    logger.warning(f"Unknown output type: {output_type} in {nb_name}, cell {cell['cell_index']}")
            
            nb_entry["cells"].append(entry)
        
        aggregated["notebooks"].append(nb_entry)
    
    return aggregated


def load_summary(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load the YAML summary file.
    
    Args:
        file_path: Path to the YAML summary file
        
    Returns:
        Dictionary containing the summary data
        
    Raises:
        FileNotFoundError: If the summary file doesn't exist
        yaml.YAMLError: If there's an error parsing the YAML
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"Summary file not found: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except yaml.YAMLError as e:
        logger.error(f"Failed to parse YAML file: {e}")
        raise


def save_results(data: Dict[str, Any], output_path: Union[str, Path]) -> None:
    """Save processed results to a JSON file.
    
    Args:
        data: Processed data to save
        output_path: Path to save the JSON file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Aggregated results written to {output_path}")
    except Exception as e:
        logger.error(f"Failed to save results: {e}")
        raise


def aggregate_notebook_summary(
    summary_path: Union[str, Path] = "results/notebook_summary.yaml",
    out_json: Union[str, Path] = "results/aggregated_results.json"
) -> Dict[str, Any]:
    """Aggregate notebook outputs into a structured format and save as JSON.
    
    This function:
    1. Loads notebook outputs from a YAML summary file
    2. Processes them, including saving images to disk
    3. Aggregates the results into a structured format
    4. Saves the aggregated results as a JSON file
    
    Args:
        summary_path: Path to the YAML summary file
        out_json: Path to save the output JSON
        
    Returns:
        The aggregated data dictionary
    """
    logger.info(f"Aggregating notebook summary from {summary_path}")
    
    try:
        # Load the summary
        summary = load_summary(summary_path)
        
        # Process the notebook outputs
        output_dir = Path(out_json).parent
        aggregated = process_notebook_outputs(summary, output_dir)
        
        # Save the results
        save_results(aggregated, out_json)
        
        return aggregated
    
    except Exception as e:
        logger.error(f"Failed to aggregate notebook summary: {e}")
        raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Aggregate notebook outputs into a structured format")
    parser.add_argument("--summary", default="results/notebook_summary.yaml", help="Path to the YAML summary file")
    parser.add_argument("--output", default="results/aggregated_results.json", help="Path to save the output JSON")
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    
    args = parser.parse_args()
    
    if args.debug:
        logger.setLevel(logging.DEBUG)
    
    aggregate_notebook_summary(args.summary, args.output)
