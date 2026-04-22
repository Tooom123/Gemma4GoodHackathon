"""
evaluate.py — Evaluate LangBridge fine-tuned model

Metrics:
  - Perplexity on validation set (before vs after fine-tuning)
  - BLEU score on translation pairs
  - Qualitative comparison: same prompt → baseline vs fine-tuned response

Usage:
  python finetune/evaluate.py \
    --base google/gemma-4-12b-it \
    --finetuned finetune/checkpoints/langbridge-v1/final \
    --val finetune/data/val.json \
    --output finetune/eval_results.json
"""

import argparse
import json
import math
import time
from pathlib import Path


QUALITATIVE_PROMPTS = [
    {
        "scenario": "prefecture",
        "prompt": "Bonjour, je veux renouveler mon titre de séjour.",
        "system": "Tu es un agent administratif à la préfecture des étrangers en France.",
    },
    {
        "scenario": "medecin",
        "prompt": "Docteur, j'ai mal partout et j'ai de la fièvre depuis deux jours.",
        "system": "Tu es un médecin généraliste dans un cabinet médical en France.",
    },
    {
        "scenario": "pharmacie",
        "prompt": "J'ai besoin un médicament pour le mal de ventre.",
        "system": "Tu es un pharmacien dans une pharmacie française.",
    },
]


def compute_perplexity(model, tokenizer, texts: list[str], max_len: int = 512) -> float:
    import torch
    model.eval()
    total_loss = 0.0
    count = 0
    with torch.no_grad():
        for text in texts:
            enc = tokenizer(text, return_tensors="pt", max_length=max_len, truncation=True)
            input_ids = enc["input_ids"].to(model.device)
            labels = input_ids.clone()
            out = model(input_ids=input_ids, labels=labels)
            total_loss += out.loss.item()
            count += 1
    return math.exp(total_loss / count) if count > 0 else float("inf")


def generate_response(model, tokenizer, system: str, prompt: str, max_new: int = 256) -> str:
    from unsloth import FastLanguageModel
    FastLanguageModel.for_inference(model)
    messages = [{"role": "user", "content": f"{system}\n\n{prompt}"}]
    text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    enc = tokenizer(text, return_tensors="pt").to(model.device)
    import torch
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new, temperature=0.7, do_sample=True)
    decoded = tokenizer.decode(out[0][enc["input_ids"].shape[1]:], skip_special_tokens=True)
    return decoded.strip()


def compute_bleu(references: list[str], hypotheses: list[str]) -> float:
    try:
        from nltk.translate.bleu_score import corpus_bleu, SmoothingFunction
        refs = [[r.split()] for r in references]
        hyps = [h.split() for h in hypotheses]
        return corpus_bleu(refs, hyps, smoothing_function=SmoothingFunction().method1)
    except ImportError:
        print("[WARN] nltk not installed, skipping BLEU. pip install nltk")
        return -1.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="google/gemma-4-12b-it")
    parser.add_argument("--finetuned", default="finetune/checkpoints/langbridge-v1/final")
    parser.add_argument("--val", default="finetune/data/val.json")
    parser.add_argument("--output", default="finetune/eval_results.json")
    parser.add_argument("--skip-perplexity", action="store_true")
    args = parser.parse_args()

    try:
        from unsloth import FastLanguageModel
        import os
    except ImportError:
        print("Install with: pip install unsloth")
        raise SystemExit(1)

    val_data = json.loads(Path(args.val).read_text())
    val_texts = [
        " ".join(t["value"] for t in ex["conversations"])
        for ex in val_data
    ]

    results: dict = {"base_model": args.base, "finetuned_model": args.finetuned}

    for label, model_path in [("baseline", args.base), ("finetuned", args.finetuned)]:
        print(f"\n=== Evaluating {label}: {model_path} ===")
        model, tokenizer = FastLanguageModel.from_pretrained(
            model_name=model_path,
            max_seq_length=2048,
            load_in_4bit=True,
            token=os.getenv("HF_TOKEN"),
        )

        if not args.skip_perplexity:
            print("Computing perplexity…")
            ppl = compute_perplexity(model, tokenizer, val_texts[:20])
            print(f"  Perplexity: {ppl:.2f}")
            results[f"{label}_perplexity"] = ppl

        print("Generating qualitative samples…")
        qualitative = []
        for p in QUALITATIVE_PROMPTS:
            t0 = time.time()
            resp = generate_response(model, tokenizer, p["system"], p["prompt"])
            elapsed = time.time() - t0
            qualitative.append({
                "scenario": p["scenario"],
                "prompt": p["prompt"],
                "response": resp,
                "latency_s": round(elapsed, 2),
            })
            print(f"  [{p['scenario']}] {resp[:80]}…")
        results[f"{label}_qualitative"] = qualitative

    # BLEU between baseline and finetuned on qualitative prompts (proxy metric)
    if "baseline_qualitative" in results and "finetuned_qualitative" in results:
        refs = [q["response"] for q in results["baseline_qualitative"]]
        hyps = [q["response"] for q in results["finetuned_qualitative"]]
        results["bleu_ft_vs_base"] = compute_bleu(refs, hyps)
        print(f"\nBLEU (finetuned vs baseline): {results['bleu_ft_vs_base']:.4f}")

    out_path = Path(args.output)
    out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
