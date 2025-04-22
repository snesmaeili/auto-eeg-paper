# auto-eeg-paper

Automated EEG → Manuscript pipeline:
1. **Run** MNE‑BIDS notebooks  
2. **Aggregate** outputs & figures  
3. **Draft** paper via GPT‑4 + Pydantic schema  
4. **Polish** figures with VLM feedback  
5. **Build** PDF with Manubot/Carbone

## Quickstart

```bash
# 1. Clone & enter
git clone git@github.com:YOUR_USERNAME/auto-eeg-paper.git
cd auto-eeg-paper

# 2. Install deps & build env
make build-env

# 3. Configure paths in configs/pipeline_config.yaml

# 4. Execute pipeline
make run-pipeline

# 5. Generate manuscript
make build-paper
