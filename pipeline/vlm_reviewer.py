import os, json, yaml, logging
from openai import OpenAI

logger = logging.getLogger(__name__)

def load_prompts(path="configs/ai_prompts.yaml"):
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def review_figure(client, prompts, img_path, caption):
    """
    Review a scientific figure using OpenAI's vision model.
    Returns a JSON report with quality assessment.
    """
    # Read image as binary
    with open(img_path, "rb") as f:
        img_data = f.read()
    
    # Use the new Responses API for image analysis
    prompt_text = prompts["vlm_review"].format(
        image=img_path,
        caption=caption
    )
    
    response = client.responses.create(
        model="gpt-4.1",
        input=[
            {"role": "user", "content": prompt_text},
            {
                "role": "user", 
                "content": [
                    {
                        "type": "input_image",
                        "image_data": {"data": img_data}
                    }
                ]
            }
        ]
    )
    
    # Parse the JSON response
    try:
        return json.loads(response.output_text)
    except json.JSONDecodeError:
        # Fallback if response isn't valid JSON
        return {
            "description": "Error: Could not parse vision model response",
            "caption_ok": False,
            "suggested_caption": caption,
            "legend_issues": "Unable to analyze",
            "clarity": "Unknown"
        }

def review_all_figures(figures_dir, draft_md, report_out):
    """
    Find all figures referenced in draft_md and send them through `review_figure`.
    Saves a JSON report.
    """
    # 1. Load draft and extract figure paths + captions
    fig_entries = []
    with open(draft_md, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip().startswith("!"):
                # Markdown image syntax: ![caption](path)
                cap, path = line.strip()[2:-1].split("](")
                fig_entries.append((path, cap))

    # 2. Initialize OpenAI client and prompts
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    prompts = load_prompts()

    # 3. Review each figure
    reviews = []
    for img_path, caption in fig_entries:
        if not os.path.exists(img_path):
            logger.warning(f"Image not found: {img_path}")
            continue
        try:
            report = review_figure(client, prompts, img_path, caption)
            report["image"] = img_path
            reviews.append(report)
        except Exception as e:
            logger.error(f"Error reviewing {img_path}: {e}")

    # 4. Save report
    os.makedirs(os.path.dirname(report_out), exist_ok=True)
    with open(report_out, "w", encoding="utf-8") as f:
        json.dump(reviews, f, indent=2)
    logger.info(f"Figure review report saved to {report_out}")
