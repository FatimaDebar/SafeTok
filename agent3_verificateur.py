"""
AGENT 3 — Vérificateur & Générateur de rapport
Input  : data/transcriptions_scored.csv
Output : data/rapport_final.csv + data/alertes.txt
"""

import pandas as pd
from datetime import datetime

INPUT_FILE   = "data/transcriptions_scored.csv"
RAPPORT_FILE = "data/rapport_final.csv"
ALERTE_FILE  = "data/alertes.txt"

def run_agent3():
    print("=" * 50)
    print("AGENT 3 — Vérificateur & Rapport")
    print("=" * 50)

    df = pd.read_csv(INPUT_FILE)
    print(f" Chargé : {len(df)} entrées\n")

    # ── Séparer DANGEROUS et SAFE ─────────────────────────
    dangerous = df[df['ai_decision'] == "DANGEROUS"].copy()
    safe      = df[df['ai_decision'] == "SAFE"].copy()

    print(f" Contenus DANGEREUX : {len(dangerous)}")
    print(f" Contenus SAFE      : {len(safe)}\n")

    # ── Niveaux de priorité selon score ───────────────────
    def get_priority(score):
        if score >= 80:
            return "CRITIQUE"
        elif score >= 50:
            return "ELEVÉ"
        else:
            return "MODÉRÉ"

    dangerous['priority'] = dangerous['ai_score'].apply(get_priority)

    # ── Trier par score décroissant ────────────────────────
    dangerous = dangerous.sort_values('ai_score', ascending=False)

    # ── Sauvegarder rapport final ──────────────────────────
    df_rapport = dangerous[['video', 'ai_score', 'priority',
                             'ai_category', 'ai_reason', 'label']].copy()
    df_rapport.to_csv(RAPPORT_FILE, index=False, encoding="utf-8")
    print(f" Rapport sauvegardé → {RAPPORT_FILE}")

    # ── Générer fichier alertes ────────────────────────────
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append(f"{'='*55}")
    lines.append(f"  SAFETOK — RAPPORT D'ALERTES")
    lines.append(f"  Généré le : {now}")
    lines.append(f"{'='*55}\n")
    lines.append(f"  Total analysé  : {len(df)}")
    lines.append(f"   DANGEREUX   : {len(dangerous)}")
    lines.append(f"   SAFE        : {len(safe)}")
    lines.append(f"\n{'='*55}")
    lines.append(f"  TOP 10 CONTENUS LES PLUS DANGEREUX")
    lines.append(f"{'='*55}\n")

    for i, row in dangerous.head(10).iterrows():
        lines.append(f"  [{row['priority']}]")
        lines.append(f"  Vidéo    : {row['video']}")
        lines.append(f"  Score    : {row['ai_score']}/100")
        lines.append(f"  Catégorie: {row['ai_category']}")
        lines.append(f"  Raison   : {row['ai_reason']}")
        lines.append(f"  Label réel: {row['label']}")
        lines.append("")

    # Stats par catégorie
    lines.append(f"{'='*55}")
    lines.append(f"  STATS PAR CATÉGORIE")
    lines.append(f"{'='*55}")
    for cat, count in dangerous['ai_category'].value_counts().items():
        lines.append(f"  {cat} : {count} vidéos")

    with open(ALERTE_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Alertes sauvegardées → {ALERTE_FILE}\n")

    # ── Affichage terminal ─────────────────────────────────
    print(" TOP 5 CONTENUS DANGEREUX :")
    print("-" * 50)
    for _, row in dangerous.head(5).iterrows():
        print(f"  {row['priority']} | Score:{row['ai_score']} | {row['ai_category']}")
        print(f"   {row['video'][:50]}")
        print(f"   {row['ai_reason']}")
        print()

    print("=" * 50)
    print(" Agent 3 terminé !")
    return dangerous

if __name__ == "__main__":
    df_dangerous = run_agent3()