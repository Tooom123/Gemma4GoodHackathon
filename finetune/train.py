"""
train.py — QLoRA fine-tuning of Gemma 4 with Unsloth

Requirements:
  pip install unsloth datasets trl torch

Hardware:
  - Recommended: NVIDIA GPU with CUDA 11.8+ (RTX 3080 or better)
  - Minimum VRAM: 16 GB (for gemma4:12b) or 40 GB (for gemma4:26b)
  - CPU-only: NOT supported for training; use Kaggle T4 GPU (free 30h/week)

Usage:
  python finetune/train.py \
    --model google/gemma-4-12b-it \
    --train finetune/data/train.json \
    --val finetune/data/val.json \
    --output finetune/checkpoints/langbridge-v1

Notes:
  - gemma-4-12b-it is used here for accessibility; swap for gemma-4-26b-it if VRAM allows
  - The model_name must match a HuggingFace Hub model ID
  - Set HF_TOKEN env var if the model requires authentication
"""

import argparse
import json
import os
from pathlib import Path


def load_conversations(path: str) -> list[dict]:
    data = json.loads(Path(path).read_text())
    return data


def format_sharegpt_to_chat(example: dict) -> dict:
    """Convert ShareGPT format to HuggingFace chat format."""
    messages = []
    for turn in example["conversations"]:
        role = "user" if turn["from"] == "human" else "assistant"
        messages.append({"role": role, "content": turn["value"]})
    return {"messages": messages}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="google/gemma-4-12b-it")
    parser.add_argument("--train", default="finetune/data/train.json")
    parser.add_argument("--val", default="finetune/data/val.json")
    parser.add_argument("--output", default="finetune/checkpoints/langbridge-v1")
    parser.add_argument("--max-seq-len", type=int, default=2048)
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--batch-size", type=int, default=2)
    parser.add_argument("--grad-accum", type=int, default=4)
    parser.add_argument("--lora-r", type=int, default=16)
    parser.add_argument("--lora-alpha", type=int, default=16)
    args = parser.parse_args()

    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import Dataset
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install unsloth trl datasets transformers torch")
        raise SystemExit(1)

    print(f"Loading model: {args.model}")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=args.model,
        max_seq_length=args.max_seq_len,
        load_in_4bit=True,
        token=os.getenv("HF_TOKEN"),
    )

    model = FastLanguageModel.get_peft_model(
        model,
        r=args.lora_r,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_alpha=args.lora_alpha,
        lora_dropout=0,
        bias="none",
        use_gradient_checkpointing=True,
        random_state=42,
    )

    train_raw = load_conversations(args.train)
    val_raw = load_conversations(args.val)
    train_ds = Dataset.from_list([format_sharegpt_to_chat(ex) for ex in train_raw])
    val_ds = Dataset.from_list([format_sharegpt_to_chat(ex) for ex in val_raw])

    def apply_chat_template(examples):
        texts = [
            tokenizer.apply_chat_template(msgs, tokenize=False, add_generation_prompt=False)
            for msgs in examples["messages"]
        ]
        return {"text": texts}

    train_ds = train_ds.map(apply_chat_template, batched=True)
    val_ds = val_ds.map(apply_chat_template, batched=True)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=train_ds,
        eval_dataset=val_ds,
        dataset_text_field="text",
        max_seq_length=args.max_seq_len,
        args=TrainingArguments(
            output_dir=str(output_dir),
            num_train_epochs=args.epochs,
            per_device_train_batch_size=args.batch_size,
            gradient_accumulation_steps=args.grad_accum,
            warmup_steps=10,
            learning_rate=2e-4,
            fp16=True,
            logging_steps=5,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            report_to="none",
        ),
    )

    print("Starting training…")
    trainer.train()

    model.save_pretrained(str(output_dir / "final"))
    tokenizer.save_pretrained(str(output_dir / "final"))
    print(f"Model saved to {output_dir}/final")


if __name__ == "__main__":
    main()
