import os

# Directories to create
dirs = [
    "notebooks",
    "pipeline",
    "templates/manubot_config",
    "configs"
]

# Files to create
files = [
    "notebooks/01_preprocessing.ipynb",
    "notebooks/02_feature_extraction.ipynb",
    "notebooks/03_statistical_analysis.ipynb",
    "pipeline/__init__.py",
    "pipeline/experiment_manager.py",
    "pipeline/notebook_runner.py",
    "pipeline/result_aggregator.py",
    "pipeline/ai_writer.py",
    "pipeline/vlm_reviewer.py",
    "templates/manuscript_schema.py",
    "templates/carbone_template.odt",
    "configs/pipeline_config.yaml",
    "configs/ai_prompts.yaml",
    "Dockerfile",
    "Makefile"
]

# Create the directories
for d in dirs:
    os.makedirs(d, exist_ok=True)

# Create the files
for f in files:
    # Ensure the directory for the file exists
    dir_path = os.path.dirname(f)
    if dir_path:
        os.makedirs(dir_path, exist_ok=True)
    # Create the file if it doesn't exist
    with open(f, 'a'):
        os.utime(f, None)

print("Project structure bootstrapped successfully!")
