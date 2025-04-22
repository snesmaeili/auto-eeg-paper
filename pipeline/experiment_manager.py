from prefect import flow, task

@task
def run_notebooks():
    import pipeline.notebook_runner as nr
    nr.main()

@task
def aggregate_results():
    import pipeline.result_aggregator as ra
    ra.aggregate_notebook_summary()

@task(name="write_manuscript")
def write_manuscript_per_section():
    """Generate a manuscript section by section using separate LLM calls.
    
    This approach avoids token limitations and allows more focused prompts
    for each section of the paper.
    """
    import pipeline.ai_writer as aw
    aw.main_per_section()

@flow(name="auto-eeg-paper")
def flow():
    """Execute the full EEG analysis and paper generation pipeline.
    
    This flow:
    1. Runs Jupyter notebooks to perform EEG analysis
    2. Aggregates results from the notebooks
    3. Generates a scientific manuscript using section-by-section LLM calls
    """
    run_notebooks()
    aggregate_results()
    write_manuscript_per_section()
