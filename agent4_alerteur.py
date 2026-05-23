"""
AGENT 4 — Alerteur final
Input  : data/rapport_final.csv
Output : affichage terminal + data/alerte_parents.txt
"""

import pandas as pd
from datetime import datetime

INPUT_FILE  = "data/rapport_final.csv"
OUTPUT_FILE = "data/alerte_parents.txt"

def send_alert_parent(video, score, category, reason):
    """Simule l'envoi d'une alerte aux parents"""
    print(f"  📱 ALERTE PARENT ENVOYÉE")
    print(f"     Vidéo    : {video[:50]}")
    print(f"     Danger   : {category} (Score: {score}/100)")
    print(f"     Raison   : {reason}")
    print()

def get_message_enfant(category):
    """Message éducatif affiché à l'enfant"""
    messages = {
        "Suicide" : "⚠️ Ce contenu aborde des sujets sensibles. Parle à un adulte de confiance si tu as besoin d'aide.",
        "Harmful" : "⚠️ Ce contenu peut être dangereux. Nous l'avons bloqué pour ta sécurité.",
        "Unknown" : "⚠️ Ce contenu a été signalé. Demande à tes parents si tu veux en savoir plus."
    }
    return messages.get(category, messages["Unknown"])

def run_agent4():
    print("=" * 55)
    print("  AGENT 4 — ALERTEUR SAFETOK")
    print("=" * 55)

    df = pd.read_csv(INPUT_FILE)
    print(f"✅ {len(df)} contenus dangereux à traiter\n")

    critique = df[df['ai_score'] >= 80]
    eleve    = df[(df['ai_score'] >= 50) & (df['ai_score'] < 80)]
    modere   = df[df['ai_score'] < 50]

    print(f"🔴 CRITIQUE ({len(critique)}) — Alerte immédiate parents")
    print(f"🟠 ÉLEVÉ   ({len(eleve)})  — Blocage + notification")
    print(f"🟡 MODÉRÉ  ({len(modere)}) — Surveillance\n")

    # ── Traiter les contenus critiques ────────────────────
    print("─" * 55)
    print("🚨 TRAITEMENT DES CAS CRITIQUES")
    print("─" * 55)

    for _, row in critique.iterrows():
        print(f"\n🔴 [{row['ai_score']}/100] {row['video'][:45]}...")
        print(f"   Catégorie : {row['ai_category']}")
        print(f"   Action    : BLOQUÉ ✋")
        send_alert_parent(
            row['video'],
            row['ai_score'],
            row['ai_category'],
            row['ai_reason']
        )
        print(f"   Message enfant : {get_message_enfant(row['ai_category'])}")
        print()

    # ── Générer rapport parents ────────────────────────────
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = []
    lines.append("=" * 55)
    lines.append("  SAFETOK — RAPPORT PARENTS")
    lines.append(f"  Date : {now}")
    lines.append("=" * 55)
    lines.append(f"\n  Contenus bloqués aujourd'hui : {len(df)}")
    lines.append(f"  🔴 Critiques : {len(critique)}")
    lines.append(f"  🟠 Élevés    : {len(eleve)}")
    lines.append(f"  🟡 Modérés   : {len(modere)}")
    lines.append("\n" + "─" * 55)
    lines.append("  DÉTAIL DES BLOCAGES")
    lines.append("─" * 55)

    for _, row in df.iterrows():
        lines.append(f"\n  Vidéo    : {row['video']}")
        lines.append(f"  Score    : {row['ai_score']}/100")
        lines.append(f"  Catégorie: {row['ai_category']}")
        lines.append(f"  Raison   : {row['ai_reason']}")
        lines.append(f"  Priorité : {row['priority']}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    # ── Résumé final ──────────────────────────────────────
    print("=" * 55)
    print("  📊 RÉSUMÉ FINAL SAFETOK")
    print("=" * 55)
    print(f"  ✅ Total analysé       : 187 vidéos")
    print(f"  🔴 Contenus bloqués    : {len(df)}")
    print(f"  📱 Alertes envoyées    : {len(critique)} parents")
    print(f"  💾 Rapport parents     : {OUTPUT_FILE}")
    print("=" * 55)
    print("\n✅ Pipeline SafeTok complet !")
    print("   Agent1 → Agent2 → Agent3 → Agent4 ✅")

if __name__ == "__main__":
    run_agent4()