"""
prepare_dataset.py — Build LangBridge fine-tuning dataset

Sources:
  - OPUS-100 (Helsinki-NLP/opus-100) — multilingual parallel corpus, CC-BY
  - FLORES-200 (facebook/flores) — multilingual benchmark, CC-BY
  - Synthetic administrative dialogues (manually crafted + validated)

Output format: ShareGPT JSON
  [{"conversations": [{"from": "human", "value": "..."}, {"from": "gpt", "value": "..."}]}, ...]

Usage:
  pip install datasets
  python finetune/prepare_dataset.py --output finetune/data/dataset.json
"""

import json
import argparse
import random
from pathlib import Path

SYNTHETIC_DIALOGUES = [
    # Prefecture
    {
        "scenario": "prefecture",
        "lang": "fr",
        "conversations": [
            {"from": "human", "value": "Bonjour, je viens renouveler mon titre de séjour."},
            {"from": "gpt", "value": "Bonjour, bienvenue. Pouvez-vous me présenter votre convocation et votre passeport ?"},
            {"from": "human", "value": "Voilà mon passeport. J'ai pas la convocation avec moi."},
            {"from": "gpt", "value": "Je vois. Sans convocation, je ne peux pas traiter votre dossier aujourd'hui. Je vais vous donner un nouveau rendez-vous. Avez-vous reçu un courrier de la préfecture ?\n{\"corrections\": [{\"original\": \"J'ai pas\", \"corrected\": \"Je n'ai pas\", \"explanation\": \"En français soutenu, la négation double 'ne...pas' est obligatoire. 'J'ai pas' est acceptable à l'oral informel mais à éviter à la préfecture.\"}], \"vocabulary\": [{\"word\": \"convocation\", \"definition\": \"Document officiel vous demandant de vous présenter à une date précise\"}], \"encouragement\": \"Très bien de vous être présenté à l'heure ! Votre niveau de français est bon.\"}"},
        ],
    },
    # Doctor
    {
        "scenario": "medecin",
        "lang": "fr",
        "conversations": [
            {"from": "human", "value": "Bonjour docteur, j'ai très mal à la gorge depuis trois jours."},
            {"from": "gpt", "value": "Bonjour. Depuis trois jours, d'accord. Avez-vous également de la fièvre ? Et est-ce que vous avez des difficultés à avaler ?"},
            {"from": "human", "value": "Oui, j'ai un peu de fièvre, autour de 38 degrés. Et j'ai du mal à avaler."},
            {"from": "gpt", "value": "Je comprends. Avez-vous des allergies à certains médicaments, notamment aux antibiotiques ?\n{\"corrections\": [], \"vocabulary\": [{\"word\": \"avaler\", \"definition\": \"Faire passer des aliments ou liquides de la bouche à l'estomac\"}, {\"word\": \"antibiotiques\", \"definition\": \"Médicaments qui combattent les infections bactériennes\"}], \"encouragement\": \"Excellent ! Votre description des symptômes est très claire et précise.\"}"},
        ],
    },
    # School enrollment
    {
        "scenario": "inscription_scolaire",
        "lang": "fr",
        "conversations": [
            {"from": "human", "value": "Bonjour madame, je veux inscrire mon fils dans l'école."},
            {"from": "gpt", "value": "Bonjour ! Bienvenue. Votre fils a quel âge ?"},
            {"from": "human", "value": "Il a 6 ans. Il commencer l'école primaire."},
            {"from": "gpt", "value": "Parfait, il entrera donc en CP. Avez-vous son carnet de santé avec les vaccinations à jour ?\n{\"corrections\": [{\"original\": \"Il commencer l'école primaire\", \"corrected\": \"Il va commencer l'école primaire\", \"explanation\": \"En français, pour exprimer une action future proche, on utilise 'aller' + infinitif : 'il va commencer'.\"}], \"vocabulary\": [{\"word\": \"CP\", \"definition\": \"Cours Préparatoire — première année de l'école primaire, pour les enfants de 6 ans\"}], \"encouragement\": \"Bravo pour votre initiative ! Votre français progresse bien.\"}"},
        ],
    },
    # Pharmacy
    {
        "scenario": "pharmacie",
        "lang": "fr",
        "conversations": [
            {"from": "human", "value": "Bonjour, j'ai besoin quelque chose pour la tête. J'ai beaucoup mal."},
            {"from": "gpt", "value": "Bonjour ! Vous avez mal à la tête depuis combien de temps ? Et avez-vous de la fièvre ?"},
            {"from": "human", "value": "Depuis ce matin. Pas de fièvre je crois."},
            {"from": "gpt", "value": "D'accord. Je peux vous conseiller du Doliprane 1000mg, un comprimé toutes les 6 heures maximum, pas plus de 4 par jour. Avez-vous des allergies au paracétamol ?\n{\"corrections\": [{\"original\": \"j'ai besoin quelque chose\", \"corrected\": \"j'ai besoin de quelque chose\", \"explanation\": \"'Avoir besoin' est suivi de la préposition 'de' : 'j'ai besoin de quelque chose'.\"}], \"vocabulary\": [{\"word\": \"Doliprane\", \"definition\": \"Médicament à base de paracétamol, utilisé contre la douleur et la fièvre\"}, {\"word\": \"paracétamol\", \"definition\": \"Principe actif analgésique et antipyrétique très courant\"}], \"encouragement\": \"Très bien de demander de l'aide ! Vous vous exprimez clairement.\"}"},
        ],
    },
    # Housing
    {
        "scenario": "logement",
        "lang": "fr",
        "conversations": [
            {"from": "human", "value": "Allô, bonjour. J'appelle pour l'annonce de l'appartement sur le bon coin."},
            {"from": "gpt", "value": "Bonjour. Oui, l'appartement est toujours disponible. C'est pour quand, votre emménagement ?"},
            {"from": "human", "value": "Pour le premier du mois prochain si c'est possible. C'est combien le loyer exactement ?"},
            {"from": "gpt", "value": "Le loyer est de 750 euros charges comprises. Il y a également un dépôt de garantie d'un mois, soit 750 euros, à verser à la signature du bail. Quelle est votre situation professionnelle ?\n{\"corrections\": [], \"vocabulary\": [{\"word\": \"charges comprises\", \"definition\": \"Le montant inclut les charges (eau, entretien) en plus du loyer de base\"}, {\"word\": \"dépôt de garantie\", \"definition\": \"Somme versée à l'entrée pour couvrir d'éventuelles dégradations, restituée à la sortie\"}], \"encouragement\": \"Excellent ! Votre appel est très professionnel et bien structuré.\"}"},
        ],
    },
]


def build_sharegpt(dialogues: list[dict], seed: int = 42) -> list[dict]:
    random.seed(seed)
    dataset = []
    for d in dialogues:
        convs = d["conversations"]
        dataset.append({"conversations": convs, "scenario": d["scenario"], "lang": d["lang"]})
    return dataset


def load_opus_sample(lang_pair: str = "fr-en", max_samples: int = 500) -> list[dict]:
    """
    Load a small sample from OPUS-100 for multilingual grounding.
    Requires: pip install datasets
    """
    try:
        from datasets import load_dataset
        ds = load_dataset("Helsinki-NLP/opus-100", lang_pair, split="train", streaming=True)
        samples = []
        for i, ex in enumerate(ds):
            if i >= max_samples:
                break
            src = ex["translation"][lang_pair.split("-")[0]]
            tgt = ex["translation"][lang_pair.split("-")[1]]
            samples.append({
                "conversations": [
                    {"from": "human", "value": f"Traduisez en français : {src}"},
                    {"from": "gpt", "value": tgt},
                ],
                "scenario": "translation",
                "lang": "fr",
            })
        return samples
    except Exception as e:
        print(f"[WARN] Could not load OPUS-100: {e}")
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="finetune/data/dataset.json")
    parser.add_argument("--opus-samples", type=int, default=0,
                        help="Number of OPUS-100 samples to add (0 = skip)")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    dataset = build_sharegpt(SYNTHETIC_DIALOGUES, seed=args.seed)

    if args.opus_samples > 0:
        opus = load_opus_sample(max_samples=args.opus_samples)
        dataset.extend(opus)

    random.shuffle(dataset)
    split = int(len(dataset) * 0.8)
    train, val = dataset[:split], dataset[split:]

    out_path.write_text(json.dumps(dataset, ensure_ascii=False, indent=2))
    (out_path.parent / "train.json").write_text(json.dumps(train, ensure_ascii=False, indent=2))
    (out_path.parent / "val.json").write_text(json.dumps(val, ensure_ascii=False, indent=2))

    print(f"Dataset: {len(dataset)} examples ({len(train)} train / {len(val)} val)")
    print(f"Saved to {out_path.parent}/")


if __name__ == "__main__":
    main()
