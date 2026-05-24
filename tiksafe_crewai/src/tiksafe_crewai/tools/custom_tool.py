from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import whisper
import easyocr
import cv2
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv(r"C:\Users\HP\Desktop\vscode\IA&APPLICATION\Projet\tiksafe_crewai\src\tiksafe_crewai\.env")

# ── Setup global ──────────────────────────────────────────
whisper_model = whisper.load_model("base")
ocr_reader    = easyocr.Reader(['en', 'fr'], gpu=False)
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# ── Tool 1 : Audio ────────────────────────────────────────
class AudioInput(BaseModel):
    video_path: str = Field(description="Path to the video file")

class AudioTranscriptionTool(BaseTool):
    name: str = "Audio Transcription Tool"
    description: str = "Transcribes audio from a TikTok video using Whisper"
    args_schema: Type[BaseModel] = AudioInput

    def _run(self, video_path: str) -> str:
        try:
            result = whisper_model.transcribe(video_path)
            return result["text"].strip()
        except Exception as e:
            return f"Error: {e}"

# ── Tool 2 : Visual ───────────────────────────────────────
class VisualInput(BaseModel):
    video_path: str = Field(description="Path to the video file")

class VisualTextTool(BaseTool):
    name: str = "Visual Text Extraction Tool"
    description: str = "Extracts on-screen text from TikTok video frames using EasyOCR"
    args_schema: Type[BaseModel] = VisualInput

    def _run(self, video_path: str) -> str:
        try:
            cap = cv2.VideoCapture(video_path)
            fps = cap.get(cv2.CAP_PROP_FPS)
            texts = []
            frame_count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % max(int(fps), 1) == 0:
                    results = ocr_reader.readtext(frame)
                    for (_, text, conf) in results:
                        if conf > 0.5 and len(text.strip()) > 2:
                            texts.append(text.strip())
                frame_count += 1
            cap.release()

            return " | ".join(set(texts)) if texts else ""
        except Exception as e:
            return f"Error: {e}"

# ── Tool 3 : Classification ───────────────────────────────
class ClassifyInput(BaseModel):
    text: str = Field(description="Combined text to classify")

class ContentClassificationTool(BaseTool):
    name: str = "Content Classification Tool"
    description: str = "Classifies TikTok content as SAFE or DANGEROUS using Groq LLM"
    args_schema: Type[BaseModel] = ClassifyInput

    def _run(self, text: str) -> str:
        try:
            prompt = f"""You are a strict TikTok content moderation expert.

FLAGGED if content contains ANY of:
- Self-harm, suicide, cutting (explicit OR implicit)
- Depression, hopelessness, worthlessness
- Dangerous stunts or violence with injury
- Drug or alcohol abuse
- Dark or triggering themes in lyrics

Transcription: \"\"\"{text[:400]}\"\"\"

Respond ONLY in this exact format:
SCORE: [0-100]
CATEGORY: [Safe OR Harmful OR Suicide]
REASON: [max 10 words]"""

            response = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                temperature=0,
                max_tokens=80
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error: {e}"

# ── Tool 4 : Alert ────────────────────────────────────────
class AlertInput(BaseModel):
    video: str  = Field(description="Video filename")
    score: int  = Field(description="Danger score 0-100")
    reason: str = Field(description="Reason for flagging")

class AlertTool(BaseTool):
    name: str = "Alert Tool"
    description: str = "Sends parent alert and blocks dangerous content"
    args_schema: Type[BaseModel] = AlertInput

    def _run(self, video: str, score: int, reason: str) -> str:
        if score >= 80:
            priority = "CRITIQUE"
        elif score >= 50:
            priority = "ELEVE"
        else:
            priority = "MODERE"

        alert = f"""
🚨 ALERTE PARENT
Vidéo    : {video}
Score    : {score}/100
Priorité : {priority}
Raison   : {reason}
Action   : BLOQUÉ ✋
"""
        print(alert)
        return alert