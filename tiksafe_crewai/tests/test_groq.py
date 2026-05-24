# Colle ce code dans test_cerebras.py
import os
from dotenv import load_dotenv
load_dotenv(r"C:\Users\HP\Desktop\vscode\IA&APPLICATION\Projet\tiksafe_crewai\src\tiksafe_crewai\.env")

from cerebras.cloud.sdk import Cerebras
client = Cerebras(api_key=os.getenv("CEREBRAS_API_KEY"))

models = client.models.list()
for m in models.data:
    print(m.id)