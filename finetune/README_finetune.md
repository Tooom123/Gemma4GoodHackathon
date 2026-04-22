# LangBridge — Fine-tuning Guide (Unsloth + QLoRA)

This directory contains reproducible scripts to fine-tune Gemma 4 on administrative dialogue data for the Unsloth prize track.

## Setup

### Hardware requirements
| Config | VRAM | Model | Speed |
|--------|------|-------|-------|
| Kaggle T4 (free) | 16 GB | gemma-4-12b-it | ~4h / epoch |
| RTX 3090 / 4090 | 24 GB | gemma-4-12b-it | ~2h / epoch |
| A100 (Colab Pro+) | 40 GB | gemma-4-26b-it | ~6h / epoch |

### Install

```bash
# Ubuntu 22.04 with CUDA 11.8+
pip install unsloth trl datasets transformers torch nltk
```

On Kaggle: select GPU T4 x2 accelerator, run in a notebook.

## Step 1 — Prepare dataset

```bash
# Synthetic dialogues only (fast, no internet needed)
python finetune/prepare_dataset.py --output finetune/data/dataset.json

# With OPUS-100 samples (requires internet + HuggingFace)
python finetune/prepare_dataset.py \
  --output finetune/data/dataset.json \
  --opus-samples 500
```

Output: `finetune/data/train.json` + `finetune/data/val.json`

## Step 2 — Train

```bash
# Gemma 4 12B (recommended for Kaggle T4)
python finetune/train.py \
  --model google/gemma-4-12b-it \
  --train finetune/data/train.json \
  --val finetune/data/val.json \
  --output finetune/checkpoints/langbridge-v1 \
  --epochs 3 \
  --batch-size 2 \
  --grad-accum 4

# Gemma 4 26B (if A100 available)
python finetune/train.py \
  --model google/gemma-4-26b-it \
  --output finetune/checkpoints/langbridge-26b
```

Set `HF_TOKEN` environment variable if the model requires authentication.

## Step 3 — Evaluate

```bash
python finetune/evaluate.py \
  --base google/gemma-4-12b-it \
  --finetuned finetune/checkpoints/langbridge-v1/final \
  --val finetune/data/val.json \
  --output finetune/eval_results.json
```

Metrics reported:
- **Perplexity** on validation set (lower = better)
- **BLEU score** (finetuned vs baseline on qualitative prompts)
- **Qualitative examples**: same prompt → baseline vs finetuned response
- **Latency**: inference time per sample

## Step 4 — Deploy with Ollama

After fine-tuning, convert and serve with Ollama:

```bash
# Convert to GGUF (requires llama.cpp)
python -m llama_cpp.convert \
  finetune/checkpoints/langbridge-v1/final \
  --outfile finetune/langbridge-v1.Q4_K_M.gguf \
  --outtype q4_k_m

# Create Ollama Modelfile
cat > Modelfile <<'EOF'
FROM ./finetune/langbridge-v1.Q4_K_M.gguf
PARAMETER temperature 0.7
PARAMETER num_ctx 2048
EOF

ollama create langbridge-v1 -f Modelfile
ollama run langbridge-v1
```

Then update the frontend model selector to use `langbridge-v1`.

## Dataset sources

| Source | License | Usage |
|--------|---------|-------|
| OPUS-100 (Helsinki-NLP) | CC-BY 4.0 | Multilingual grounding |
| FLORES-200 (Meta) | CC-BY-SA 4.0 | Multilingual benchmark |
| Synthetic dialogues | Apache 2.0 | Administrative scenarios |

## Expected results (indicative)

| Metric | Baseline gemma-4-12b | Fine-tuned |
|--------|----------------------|------------|
| Perplexity (admin dialogues) | ~45 | ~18 |
| JSON format compliance | ~60% | ~95% |
| Bureaucratic role consistency | subjective ↑ | subjective ↑↑ |
