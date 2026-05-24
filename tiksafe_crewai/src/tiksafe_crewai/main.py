import os
import json
import re
import pandas as pd
from tiksafe_crewai.crew import TiksafeCrewai

os.makedirs("output", exist_ok=True)

def parse_result(result_str: str, video: str, category: str) -> dict:
    """Extraire les infos du résultat de l'agent"""
    result_str = str(result_str)

    # Détecter le label
    if "DANGEROUS" in result_str or "CRITIQUE" in result_str or "FLAGGED" in result_str:
        label = "FLAGGED"
    else:
        label = "SAFE"

    # Détecter la priorité
    if "CRITIQUE" in result_str:
        priority = "CRITIQUE"
    elif "ELEVE" in result_str:
        priority = "ELEVE"
    elif "MODERE" in result_str:
        priority = "MODERE"
    else:
        priority = "N/A"

    # Extraire le score
    score_match = re.search(r"Score\s*:\s*(\d+)/100", result_str)
    score = int(score_match.group(1)) if score_match else 0

    # Extraire la raison
    reason_match = re.search(r"Raison\s*:\s*(.+?)(?:\n|Action)", result_str)
    reason = reason_match.group(1).strip() if reason_match else "N/A"

    return {
        "video": video,
        "category_real": category,
        "predicted_label": label,
        "priority": priority,
        "score": score,
        "reason": reason,
        "correct": (label == "FLAGGED") == (category != "Safe")
    }

def run_demo(csv_path: str, n_videos: int = 5):
    """Démo du pipeline CrewAI sur N vidéos"""

    df = pd.read_csv(csv_path)
    print(f"📂 {len(df)} vidéos disponibles — test sur {n_videos}")

    results = []

    for i in range(n_videos):
        item = df.iloc[i]
        print(f"\n{'='*60}")
        print(f"[{i+1}/{n_videos}] 📹 {item['video']}")
        print(f"   Catégorie réelle : {item['category']}")
        print(f"   Texte : {str(item['text_clean'])[:80]}...")

        try:
            result = TiksafeCrewai().crew().kickoff(
                inputs={
                    "video": str(item["video"]),
                    "text": str(item["text_clean"]),
                    "category": str(item["category"])
                }
            )

            # Parser le résultat
            parsed = parse_result(
                result_str=str(result),
                video=str(item["video"]),
                category=str(item["category"])
            )
            results.append(parsed)

            print(f"   ✅ Label: {parsed['predicted_label']} | Priority: {parsed['priority']} | Score: {parsed['score']}/100")
            print(f"   Correct: {'✅' if parsed['correct'] else '❌'}")

        except Exception as e:
            print(f"\n❌ Erreur : {e}")
            results.append({
                "video": str(item["video"]),
                "category_real": str(item["category"]),
                "predicted_label": "ERROR",
                "priority": "N/A",
                "score": 0,
                "reason": str(e),
                "correct": False
            })

    # ── Stats finales ─────────────────────────────────────
    total     = len(results)
    correct   = sum(1 for r in results if r["correct"])
    flagged   = sum(1 for r in results if r["predicted_label"] == "FLAGGED")
    safe      = sum(1 for r in results if r["predicted_label"] == "SAFE")
    errors    = sum(1 for r in results if r["predicted_label"] == "ERROR")
    accuracy  = round(correct / total * 100, 1) if total > 0 else 0

    summary = {
        "total_videos": total,
        "flagged": flagged,
        "safe": safe,
        "errors": errors,
        "correct_predictions": correct,
        "accuracy": f"{accuracy}%"
    }

    # ── Sauvegarder JSON organisé ─────────────────────────
    output = {
        "summary": summary,
        "results": results
    }

    output_path = "output/crewai_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # ── Afficher résumé ───────────────────────────────────
    print(f"\n{'='*60}")
    print(f"🏆 DÉMO CREWAI TERMINÉE !")
    print(f"{'='*60}")
    print(f"   Vidéos testées     : {total}")
    print(f"   FLAGGED détectés   : {flagged}")
    print(f"   SAFE               : {safe}")
    print(f"   Prédictions justes : {correct}/{total}")
    print(f"   Accuracy           : {accuracy}%")
    print(f"   Résultats          : {output_path}")
    print(f"{'='*60}")

if __name__ == "__main__":
    csv_path = r"C:\Users\HP\Desktop\vscode\IA&APPLICATION\Projet\SafeTok\data\transcriptions_clean.csv"
    run_demo(csv_path, n_videos=5)