import os
import yaml
import nbformat
from nbformat import read
from nbconvert.preprocessors import ExecutePreprocessor
from nbclient.exceptions import CellExecutionError

def load_config(path="configs/pipeline_config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_notebook(nb_path, out_path, timeout=600):
    """Execute a notebook and save its output."""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(nb_path, "r", encoding="utf-8") as f:
        nb = read(f, as_version=nbformat.NO_CONVERT)

    ep = ExecutePreprocessor(timeout=timeout, kernel_name="python3")
    ep.preprocess(nb, {'metadata': {'path': os.path.dirname(nb_path) or './'}})

    with open(out_path, "w", encoding="utf-8") as f:
        nbformat.write(nb, f)
    return nb

def load_executed_notebook(path):
    """Load an already executed notebook for parsing."""
    with open(path, "r", encoding="utf-8") as f:
        return nbformat.read(f, as_version=4)

def display_notebook_content(nb):
    """Display the full content of a notebook in the terminal."""
    for idx, cell in enumerate(nb.cells):
        cell_type = cell.cell_type.upper()
        source = cell.source
        
        print(f"\n{'='*80}\nCELL {idx} [{cell_type}]\n{'='*80}")
        print(source)
        
        if hasattr(cell, "outputs") and cell.outputs:
            print(f"\n{'-'*40} OUTPUTS {'-'*40}")
            for out in cell.outputs:
                if out.output_type == 'stream':
                    print(f"[STREAM]:\n{out.text}")
                elif out.output_type in ('execute_result', 'display_data'):
                    data = out.get('data', {})
                    if 'text/plain' in data:
                        print(f"[TEXT]:\n{data['text/plain']}")
                    if 'image/png' in data:
                        print(f"[IMAGE]: Image data available (base64 encoded, not displayed in terminal)")
                elif out.output_type == 'error':
                    print(f"[ERROR]: {out.ename}: {out.evalue}")
                    for tb_line in out.traceback:
                        print(tb_line)

def parse_notebook_outputs(nb):
    """
    Collect all cell outputs (text and images).
    Returns a list of {cell_index, outputs: [...]}
    """
    results = []
    for idx, cell in enumerate(nb.cells):
        if not hasattr(cell, "outputs"):
            continue
        cell_outs = []
        for out in cell.outputs:
            if out.output_type == 'stream':
                cell_outs.append({'type':'text', 'text': out.text})
            elif out.output_type in ('execute_result', 'display_data'):
                data = out.get('data', {})
                if 'text/plain' in data:
                    cell_outs.append({'type':'text', 'text': data['text/plain']})
                if 'image/png' in data:
                    cell_outs.append({'type':'image', 'data': data['image/png']})
            elif out.output_type == 'error':
                cell_outs.append({'type':'error', 'ename': out.ename, 'evalue': out.evalue, 'traceback': out.traceback})
        if cell_outs:
            results.append({'cell_index': idx, 'outputs': cell_outs})
    return results

def main():
    cfg = load_config()
    notebooks = cfg.get("notebooks", [])
    
    # Check if notebooks exist or create them if needed
    for nb_path in notebooks:
        if not os.path.exists(nb_path):
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(nb_path), exist_ok=True)
            
            # Create empty notebook if it doesn't exist
            print(f"Notebook {nb_path} not found. Creating empty notebook.")
            nb = nbformat.v4.new_notebook()
            with open(nb_path, "w", encoding="utf-8") as f:
                nbformat.write(nb, f)
    
    results_dir = cfg.get("output", {}).get("results_dir", "results")
    summary = {}

    for nb in notebooks:
        basename = os.path.basename(nb)
        out_nb = os.path.join(results_dir, "notebooks", basename)
        print(f"\n\n{'*'*100}\nProcessing {nb}\n{'*'*100}")

        try:
            if os.path.exists(out_nb):
                print(f"Loading existing executed notebook: {out_nb}")
                nb_obj = load_executed_notebook(out_nb)
            else:
                print(f"Running notebook: {nb}")
                try:
                    nb_obj = run_notebook(nb, out_nb)
                    print(f"Executed and saved to {out_nb}")
                except (CellExecutionError, FileNotFoundError) as e:
                    print(f"Failed to process {nb}: {e}")
                    continue

            # Display the full notebook content
            print(f"\nDisplaying content of {basename}:")
            display_notebook_content(nb_obj)
            
            # Parse and store outputs
            summary[basename] = parse_notebook_outputs(nb_obj)
            
        except Exception as e:
            print(f"Error processing notebook {nb}: {e}")
            continue

    # Write a YAML summary for downstream steps
    summary_path = os.path.join(results_dir, "notebook_summary.yaml")
    os.makedirs(os.path.dirname(summary_path), exist_ok=True)
    with open(summary_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(summary, f)

    print(f"\nNotebook processing complete. Summary at {summary_path}")

if __name__ == "__main__":
    main()
