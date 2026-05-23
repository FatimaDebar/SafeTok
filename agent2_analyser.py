"""
AGENT 2 — Analyseur amélioré
Input  : data/transcriptions_clean.csv
Output : data/transcriptions_scored.csv
"""

import pandas as pd
import os
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
INPUT_FILE  = "data/transcriptions_clean.csv"
OUTPUT_FILE = "data/transcriptions_scored.csv"

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def build_prompt(text):
    return f"""You are a TikTok content safety classifier for protecting children.

Analyze this TikTok transcription. It may be in ANY language.
Look for ANY signs of: self-harm, suicide, depression, dangerous challenges, drug abuse, violence.

Transcription:
\"\"\"{text[:400]}\"\"\"

Respond ONLY in this exact format:
SCORE: [number 0-100, where 0=totally safe, 100=extremely dangerous]
CATEGORY: [Safe OR Harmful OR Suicide]
REASON: [max 10 words in English]
"""

# ─── VERSION SIMPLE QUI MARCHE ────────────────────────────
def score_to_decision(score):
    if score >= 50:
        return "DANGEROUS"
    return "SAFE"

def analyse_text(text):
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": build_prompt(text)}],
            temperature=0,
            max_tokens=80,
        )
        result = response.choices[0].message.content.strip()
        return parse_result(result)
    except Exception as e:
        print(f"  ⚠️ Erreur : {e}")
        return {"score": 0, "ai_category": "Error", "ai_decision": "SAFE", "reason": str(e)}

def parse_result(text):
    result = {"score": 0, "ai_category": "Unknown", "ai_decision": "SAFE", "reason": ""}
    for line in text.split("\n"):
        line = line.strip()
        if line.startswith("SCORE:"):
            try:
                result["score"] = int(line.replace("SCORE:", "").strip())
            except:
                result["score"] = 0
        elif line.startswith("CATEGORY:"):
            result["ai_category"] = line.replace("CATEGORY:", "").strip()
        elif line.startswith("REASON:"):
            result["reason"] = line.replace("REASON:", "").strip()

    result["ai_decision"] = score_to_decision(result["score"])
    return result

def run_agent2():
    print("=" * 50)
    print("AGENT 2 — Analyse")
    print("=" * 50)

    df = pd.read_csv(INPUT_FILE)
    print(f"✅ Chargé : {len(df)} entrées\n")

    scores, categories, decisions, reasons = [], [], [], []

    for i, row in df.iterrows():
        print(f"[{i+1}/{len(df)}] {row['video'][:45]}...")
        result = analyse_text(row['text_clean'])
        scores.append(result["score"])
        categories.append(result["ai_category"])
        decisions.append(result["ai_decision"])
        reasons.append(result["reason"])
        print(f"  → SCORE:{result['score']} | {result['ai_decision']} | {result['ai_category']}")
        time.sleep(0.3)

    df['ai_score']    = scores
    df['ai_category'] = categories
    df['ai_decision'] = decisions
    df['ai_reason']   = reasons

    correct  = (df['ai_decision'] == df['label']).sum()
    accuracy = round(correct / len(df) * 100, 2)
    print(f"\n🎯 Accuracy : {accuracy}% ({correct}/{len(df)})")
    print(f"\n📊 Confusion rapide :")
    print(df.groupby(['label', 'ai_decision']).size().to_string())

    df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8")
    print(f"\n💾 Sauvegardé → {OUTPUT_FILE}")
    print("=" * 50)
    return df

if __name__ == "__main__":
    df = run_agent2()