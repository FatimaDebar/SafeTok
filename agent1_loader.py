"""
AGENT 1 — Récupérateur & Nettoyeur de transcriptions TikTok
Input  : data/transcriptions_200.json
Output : data/transcriptions_clean.csv
"""

import json
import pandas as pd
import re

# ─── CONFIG ───────────────────────────────────────────────
INPUT_FILE  = "data/transcriptions_200.json"
OUTPUT_FILE = "data/transcriptions_clean.csv"

# Bruit UI TikTok à supprimer
UI_NOISE = ["tiktok", "following", "followers", "likes", "share", "comment",
            "duet", "stitch", "fyp", "foryou", "foryoupage", "viral"]

# ─── STEP 1 : Charger le JSON ─────────────────────────────
def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    print(f" Chargé : {len(df)} entrées")
    return df

# ─── STEP 2 : Nettoyer le texte ───────────────────────────
def clean_text(text):
    if not isinstance(text, str):
        return ""

    # Supprimer caractères spéciaux
    text = re.sub(r'[|@#]', ' ', text)

    # Supprimer lettres répétées (Woooow → Wow)
    text = re.sub(r'(.)\1{3,}', r'\1\1', text)

    # Supprimer mots répétés 3+ fois (mot mot mot → mot)
    text = re.sub(r'\b(\w+)\b(?:\s+\1\b){2,}', r'\1', text, flags=re.IGNORECASE)

    # Supprimer nombres seuls courts
    text = re.sub(r'\b\d{1,2}\b', '', text)

    # Supprimer bruit UI TikTok
    words = text.split()
    words = [w for w in words if w.lower() not in UI_NOISE]
    text = ' '.join(words)

    # Nettoyer espaces
    text = re.sub(r'\s+', ' ', text).strip()

    return text

# ─── STEP 3 : Fusionner audio + visual ────────────────────
def build_final_text(row):
    audio  = clean_text(row['audio_text'])
    visual = clean_text(row['visual_text'])

    # Ignorer si trop court — pas de contenu utile
    if len(audio) < 10:
        audio = ""
    if len(visual) < 10:
        visual = ""

    if audio and visual:
        return f"{audio} {visual}"
    elif audio:
        return audio
    elif visual:
        return visual
    else:
        return ""

# ─── STEP 4 : Pipeline principal ──────────────────────────
def run_agent1():
    print("=" * 50)
    print("AGENT 1 — Chargement & Nettoyage")
    print("=" * 50)

    df = load_data(INPUT_FILE)

    df['text_clean'] = df.apply(build_final_text, axis=1)

    before = len(df)
    df = df[df['text_clean'].str.strip() != ""].reset_index(drop=True)
    print(f"  Supprimé : {before - len(df)} lignes vides ou bruit")

    df_clean = df[['video', 'category', 'label', 'text_clean']].copy()

    print(f"\nDistribution des labels :")
    print(df_clean['label'].value_counts().to_string())
    print(f"\n Distribution des catégories :")
    print(df_clean['category'].value_counts().to_string())
    print(f"\n Total propre : {len(df_clean)} entrées")

    df_clean.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n Sauvegardé → {OUTPUT_FILE}")
    print("=" * 50)

    return df_clean

# ─── RUN ──────────────────────────────────────────────────
if __name__ == "__main__":
    df = run_agent1()
    print("\n Aperçu (5 premières lignes) :")
    print(df[['label', 'category', 'text_clean']].head().to_string())