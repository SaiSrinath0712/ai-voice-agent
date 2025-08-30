# AI Voice Chat Agent – Khansaar Universe
An intelligent AI voice assistant that interacts using spoken queries with real-time responses, powered by AssemblyAI, Gemini, Murf, and OpenWeatherMap APIs.
## Features
Voice-Enabled Chat: Record your voice via browser, and the system transcribes and responds intelligently.

Multi-API Integration: Uses AssemblyAI (speech-to-text), Gemini (LLM responses), Murf (text-to-speech), and OpenWeatherMap (weather info).

Customizable API Keys: Enter your own keys or fallback on server environment keys.

Persona-Driven Responses: Replies are delivered in a calm, authoritative voice persona named “Deva.”

Weather Awareness: Recognizes location keywords and fetches live weather updates.

Audio Playback: Synthesized speech plays back responses directly in the browser.

Session Chat History: Maintains conversation context for each chat session.


Technology Stack
Layer	Tool/Service	Purpose
Frontend	HTML, CSS, JavaScript	UI, audio recording & playback
Backend	FastAPI	API server & logic handling
NLP	spaCy	Entity extraction (locations)
Language Model	Gemini (Google)	Generate context-aware replies
Speech-to-Text	AssemblyAI	Convert speech input to text
Text-to-Speech	Murf	Convert replies to audio
Weather Data	OpenWeatherMap	Provide live weather information
Getting Started
Prerequisites
Python 3.10+

API keys from:

AssemblyAI

Murf

Gemini

OpenWeatherMap

Installation
Clone the repository:

bash
git clone https://github.com/YOUR-USERNAME/ai-voice-agent.git
cd ai-voice-agent
Install dependencies:

bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
Set up environment variables in .env file:

text
ASSEMBLYAI_API_KEY=your_assemblyai_key
MURF_API_KEY=your_murf_key
GEMINI_API_KEY=your_gemini_key
WEATHER_API_KEY=your_openweather_key
Start the backend server:

bash
uvicorn main:app --reload
Open your browser at:

text
http://localhost:8000/
Usage
Enter your API keys on the login page.

Click Start Recording 🎤 to ask your query.

View responses as text and listen to audio playback.

Ask for weather updates by mentioning locations.

Click Sign Out to clear your session data.

API Endpoints
POST /agent/chat/{session_id}
Accepts audio file and API keys, returns transcription, AI reply, and speech audio URL.

GET /
Serves the chat UI (index.html).

GET /favicon.ico
Serves the favicon.

Project Structure
text
ai-voice-agent/
├── main.py           # Backend API and logic
├── static/           # Frontend HTML, CSS, JS assets
├── uploads/          # Temporary audio storage
├── README.md         # Project documentation
├── .env              # Environment variables (not in repo)
Additional Information
Persona “Deva” ensures calm and authoritative responses.

SpaCy NLP detects location entities from queries.

Secure handling of API keys; no keys stored permanently on client.

Session-based history supports conversational context.
