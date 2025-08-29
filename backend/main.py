import os
import logging
import tempfile
import shutil
from datetime import datetime
import httpx
import spacy
from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Path as ApiPath
from fastapi.responses import FileResponse, Response
from fastapi.staticfiles import StaticFiles
from pathlib import Path as FSPath
from dotenv import load_dotenv
import assemblyai as aai
import pytz
from google import genai
from google.genai import types

# Load environment variables
load_dotenv()

# Logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()

# Load spaCy English model once at startup
nlp = spacy.load("en_core_web_sm")

# Load default API keys from environment variables
ASSEMBLYAI_API_KEY = os.getenv("ASSEMBLYAI_API_KEY")
MURF_API_KEY = os.getenv("MURF_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

for key_name, key in [
    ("ASSEMBLYAI_API_KEY", ASSEMBLYAI_API_KEY),
    ("MURF_API_KEY", MURF_API_KEY),
    ("GEMINI_API_KEY", GEMINI_API_KEY),
    ("WEATHER_API_KEY", WEATHER_API_KEY),
]:
    if not key:
        logger.warning(f"{key_name} not set in environment — fallback to user input required")

UPLOADS_DIR = FSPath("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)

STATIC_DIR = FSPath("static")
STATIC_DIR.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/")
async def root():
    return FileResponse(STATIC_DIR / "index.html")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    favicon_path = STATIC_DIR / "favicon.ico"
    if favicon_path.exists():
        return FileResponse(favicon_path)
    return Response(status_code=204)

PERSONA_PROMPT = (
    "You are Deva: a calm, stoic, and unwavering one-man army. "
    "You speak with precision and power. When asked factual or general questions, you answer them concisely and directly. "
    "Avoid idle chatter, but always provide clear, helpful responses to questions. "
    "Maintain a confident and authoritative tone."
)

chat_history_store = {}

def get_chat_history(session_id):
    return chat_history_store.get(session_id, [])

def add_message_to_history(session_id, role, text):
    if session_id not in chat_history_store:
        chat_history_store[session_id] = []
    chat_history_store[session_id].append({"role": role, "text": text})

def build_gemini_contents(session_id):
    history = get_chat_history(session_id)
    contents = []
    for msg in history:
        contents.append({"role": msg["role"], "parts": [{"text": msg["text"]}]})
    return contents

weather_function = {
    "name": "get_current_temperature",
    "description": "Gets the current temperature and weather description for a given location.",
    "parameters": {
        "type": "object",
        "properties": {
            "location": {
                "type": "string",
                "description": "The city name, e.g. London",
            },
        },
        "required": ["location"],
    },
}
india_datetime_function = {
    "name": "get_india_datetime",
    "description": "Gets the current date and time in India timezone.",
    "parameters": {"type": "object", "properties": {}, "required": []},
}
london_datetime_function = {
    "name": "get_london_datetime",
    "description": "Gets the current date and time in London timezone.",
    "parameters": {"type": "object", "properties": {}, "required": []},
}

import string

def extract_location(text: str) -> str | None:
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "GPE":
            # Remove trailing punctuation from city name
            return ent.text.strip(string.punctuation)
    # Fallback: extract after 'of'
    words = text.split()
    for i, word in enumerate(words):
        if word.lower() == "of" and i + 1 < len(words):
            return words[i + 1].strip(string.punctuation)
    return None



async def get_current_temperature(location: str, api_key: str) -> dict:
    indian_cities = {
        "Hyderabad", "Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata",
        "Ahmedabad", "Pune", "Surat", "Jaipur", "Lucknow", "Kanpur",
    }
    city_name = location.split(",")[0].strip()
    if city_name in indian_cities and "," not in location:
        location = f"{city_name},IN"
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {"q": location, "appid": api_key, "units": "metric"}
    async with httpx.AsyncClient(timeout=10) as client:
        try:
            resp = await client.get(url, params=params)
            data = resp.json()
            if resp.status_code != 200:
                error_msg = data.get("message", f"HTTP {resp.status_code}")
                return {"error": f"Weather data for {city_name} is unavailable. {error_msg}"}
            temperature = data["main"]["temp"]
            description = data["weather"][0]["description"]
            humidity = data["main"]["humidity"]
            wind_speed = data["wind"]["speed"]
            city = data["name"]
            return {
                "location": city,
                "temperature": temperature,
                "unit": "Celsius",
                "description": description,
                "humidity": humidity,
                "wind_speed": wind_speed,
            }
        except Exception as e:
            return {"error": f"Weather data for {city_name} is unavailable. {str(e)}"}

def get_india_datetime() -> dict:
    india_tz = pytz.timezone("Asia/Kolkata")
    now_india = datetime.now(india_tz)
    dt_string = now_india.strftime("%Y-%m-%d %H:%M:%S %Z")
    return {"datetime": dt_string}

def get_london_datetime() -> dict:
    london_tz = pytz.timezone("Europe/London")
    now_london = datetime.now(london_tz)
    dt_string = now_london.strftime("%Y-%m-%d %H:%M:%S %Z")
    return {"datetime": dt_string}

@app.post("/agent/chat/{session_id}")
async def chat_with_history(
    session_id: str = ApiPath(...),
    file: UploadFile = File(...),
    assemblyai_api_key: str = Form(None),
    murf_api_key: str = Form(None),
    gemini_api_key: str = Form(None),
    weather_api_key: str = Form(None),
):
    # Use user provided keys or fallback to environment keys
    assemblyai_key = assemblyai_api_key or ASSEMBLYAI_API_KEY
    murf_key = murf_api_key or MURF_API_KEY
    gemini_key = gemini_api_key or GEMINI_API_KEY
    weather_key = weather_api_key or WEATHER_API_KEY

    aai.settings.api_key = assemblyai_key
    transcriber = aai.Transcriber()

    with tempfile.NamedTemporaryFile(dir=UPLOADS_DIR, suffix=".wav", delete=False) as temp_audio:
        shutil.copyfileobj(file.file, temp_audio)
        temp_path = temp_audio.name
    logger.debug(f"Saved uploaded audio to {temp_path}")

    try:
        transcript = transcriber.transcribe(temp_path)
        if transcript.error or not transcript.text or not transcript.text.strip():
            raise HTTPException(status_code=400, detail=f"Transcription error: {transcript.error or 'Empty text'}")
        user_text = transcript.text.strip()
        logger.debug(f"Transcript: {user_text}")

        add_message_to_history(session_id, "user", user_text)

        if "weather" in user_text.lower():
            city = extract_location(user_text)
            if not city:
                city = "Delhi"
            weather = await get_current_temperature(city, weather_key)
            if "error" in weather:
                display = f"Weather data for {city.title()} is unavailable."
            else:
                display = (
                    f"Weather in {city.title()}: "
                    f"{weather['description']}, {weather['temperature']}°C. "
                    f"Humidity: {weather['humidity']}%. "
                    f"Wind speed: {weather['wind_speed']:.1f} m/s."
                )
            add_message_to_history(session_id, "model", display)

            audio_url = None
            try:
                async with httpx.AsyncClient(timeout=60) as client:
                    resp = await client.post(
                        "https://api.murf.ai/v1/speech/generate",
                        json={"text": display, "voice_id": "en-US-marcus", "audio_format": "mp3"},
                        headers={"api-key": murf_key, "Content-Type": "application/json"},
                    )
                    resp.raise_for_status()
                    audio_url = resp.json().get("audioFile") or resp.json().get("audio_url")
            except Exception as e:
                logger.warning(f"Murf TTS failed for weather: {e}")

            return {"user_text": user_text, "llm_text": display, "audio_url": audio_url}

        client = genai.Client(api_key=gemini_key)
        tools = types.Tool(function_declarations=[weather_function, india_datetime_function, london_datetime_function])
        config = types.GenerateContentConfig(tools=[tools], temperature=0.5)  # Higher temperature for flexibility
        contents = [{"role": "model", "parts": [{"text": PERSONA_PROMPT}]}] + build_gemini_contents(session_id)
        contents.append({"role": "user", "parts": [{"text": user_text}]})

        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=contents, config=config
        )

        first_part = response.candidates[0].content.parts[0]
        if first_part.function_call:
            fn_call = first_part.function_call
            args = fn_call.args or {}
            if fn_call.name == "get_current_temperature":
                result = await get_current_temperature(**args, api_key=weather_key)
            elif fn_call.name == "get_india_datetime":
                result = get_india_datetime()
            elif fn_call.name == "get_london_datetime":
                result = get_london_datetime()
            else:
                result = {"error": "Unknown function"}
            function_response_part = types.Part.from_function_response(name=fn_call.name, response=result)
            contents.append(response.candidates[0].content)
            contents.append(types.Content(role="user", parts=[function_response_part]))
            final_response = client.models.generate_content(
                model="gemini-2.5-flash", config=config, contents=contents
            )
            llm_reply = final_response.text
        else:
            llm_reply = first_part.text

        add_message_to_history(session_id, "model", llm_reply)
        logger.debug(f"Gemini reply: {llm_reply}")

        audio_url = None
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                resp = await client.post(
                    "https://api.murf.ai/v1/speech/generate",
                    json={"text": llm_reply, "voice_id": "en-US-marcus", "audio_format": "mp3"},
                    headers={"api-key": murf_key, "Content-Type": "application/json"},
                )
                resp.raise_for_status()
                audio_url = resp.json().get("audioFile") or resp.json().get("audio_url")
        except Exception as e:
            logger.warning(f"Murf TTS failed for Gemini reply: {e}")

        return {"user_text": user_text, "llm_text": llm_reply, "audio_url": audio_url}

    finally:
        try:
            os.unlink(temp_path)
        except Exception:
            pass