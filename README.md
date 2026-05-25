----- TikSafe -----

TikSafe is an intelligent multi-agent pipeline that automatically detects dangerous content on TikTok (self-harm, suicide, violence, harmful behavior) using audio transcription and visual text extraction combined with LLM classification.

---> Project Overview:
This project implements two versions of the same pipeline:

Version 1 : Sequential Python pipeline with 4 specialized agents
Version 2 : CrewAI + Bonsai hybrid architecture with cognitive agents and reactive tools

---> Configuration:
Create a .env file in the project root:
GROQ_API_KEY=your_groq_api_key
CEREBRAS_API_KEY=your_cerebras_api_key
Get free API keys:
Groq : https://console.groq.com
Cerebras : https://cloud.cerebras.ai

---> How to Run:
++ Version 1 - Python Pipeline - Run agents sequentially:

-- Step 1 - Load and clean data: python agent1_loader.py

-- Step 2 - Analyze content with LLM: python agent2_analyser.py

-- Step 3 - Generate verification report: python agent3_verificateur.py

-- Step 4 - Send parent alerts: python agent4_alerteur.py

-- Step 5 - Launch dashboard: streamlit run dashboard.py

++ Version 2 - CrewAI + Bonsai Pipeline:
bashcd tiksafe_crewai/src
python -m tiksafe_crewai.main

Output is saved to: tiksafe_crewai/src/output/crewai_results.json
