# AI Voice Chat Agent – Khansaar Universe

An intelligent AI voice assistant that interacts with users through spoken queries, providing real-time responses powered by AssemblyAI, Gemini, Murf, and OpenWeatherMap APIs.
---

## Features

- **Voice-Enabled Chat:** Users speak directly to the app; speech is transcribed and understood.
- **Multi-API Integration:** Combines AssemblyAI (speech-to-text), Gemini (LLM), Murf (text-to-speech), and OpenWeatherMap (live weather data).
- **Customizable API Keys:** Users can input their own keys or fallback to server-stored keys.
- **Persona-Driven Replies:** The assistant speaks as “Deva,” a calm and authoritative persona.
- **Weather Awareness:** Detects mentioned locations and provides live weather updates.
- **Audio Playback:** Synthesized responses play back within the browser.
- **Session-Based Chat History:** Maintains context for ongoing conversations.
---

## Technology Stack

| Layer          | Tool/Service         | Purpose                          |
|----------------|---------------------|---------------------------------|
| Frontend       | HTML, CSS, JavaScript | UI, voice recording & playback  |
| Backend        | FastAPI             | API server and business logic   |
| NLP            | spaCy               | Location entity recognition     |
| Language Model | Gemini (Google)     | Context-aware replies           |
| Speech-to-Text | AssemblyAI          | Transcribe user speech          |
| Text-to-Speech | Murf                | Generate audio responses        |
| Weather Data   | OpenWeatherMap      | Fetch live weather information  |
---

## Getting Started

### Prerequisites

- Python 3.10 or higher
- API keys for:
  - AssemblyAI
  - Murf
  - Gemini
  - OpenWeatherMap

### Installation

1. Clone the repository:
git clone  https://github.com/SaiSrinath0712/ai-voice-agent
cd ai-voice-agent

2. Install Python dependencies:
pip install -r requirements.txt
python -m spacy download en_core_web_sm

3. Set up environment variables in `.env` file:
ASSEMBLYAI_API_KEY=your_assemblyai_key
MURF_API_KEY=your_murf_key
GEMINI_API_KEY=your_gemini_key
WEATHER_API_KEY=your_openweather_key

4. Start the backend server:
uvicorn main:app --reload

5. Open your browser and visit:
http://localhost:8000/
---
## Usage

- Enter your API keys on the login page.
- Click **Start Recording 🎤** and speak your query.
- Receive both text and audio responses.
- Ask for weather updates by mentioning city names.
- Use **Sign Out** to clear session data and keys.
---

## API Endpoints

- `POST /agent/chat/{session_id}`  
Accepts an audio file and API keys, returns transcription, AI response, and TTS audio URL.

- `GET /`  
Serves the main chat UI (index.html).

- `GET /favicon.ico`  
Serves the favicon.
---

## Project Structure

ai-voice-agent/
├── main.py # Backend API and logic
├── static/ # Frontend assets (HTML, CSS, JS)
├── uploads/ # Temporary audio file storage
├── README.md # This documentation file
├── .env # Environment variable file (not committed to repo)

---
## Additional Information

- The AI persona “Deva” ensures calm and precise replies.
- The spaCy NLP model detects locations mentioned in queries for weather.
- API keys are handled securely; no permanent storage on client.
- Sessions maintain conversation context for a smooth chat experience.
---

## Contributing

Contributions and feedback are welcome! Please open issues or submit pull requests on GitHub to improve the project.
---


