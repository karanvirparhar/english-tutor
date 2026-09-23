# 9th Grade English Writing Tutor

A Streamlit app that helps 9th grade students improve writing through tutoring conversations, assignment feedback, vocabulary suggestions, and rubric-based grading.

## Features

- Chat with a 9th grade English writing tutor
- Submit argumentative, informative, narrative, or other writing for feedback
- Receive rubric-based grades, revision suggestions, and vocabulary recommendations
- Review submitted work during the current Streamlit session
- Use writing tips, essay structure guidance, and a revision checklist

## Requirements

- Python 3.9 or newer
- One supported language model provider:
	- Ollama, with a locally downloaded model (default)
	- OpenAI, with an API key
	- Gemini, with an API key

Ollama must be installed and running only when you use the Ollama provider.

## Setup

From the project directory:

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configure the environment

1. Copy `.env_sample` and name the copy `.env`:

```bash
cp .env_sample .env
```

2. Open `.env` and set the variables for the provider you want to use.

3. Configure one provider:
   - **Ollama:** Install and start Ollama, then run `ollama pull gemma4:31b`. If needed, set a different model in `OLLAMA_MODEL`.
   - **OpenAI:** Set `LLM_PROVIDER=openai` and add your `OPENAI_API_KEY`.
   - **Gemini:** Set `LLM_PROVIDER=gemini` and add your `GEMINI_API_KEY`.

## Run the app

```bash
streamlit run st_english_tutor.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## LLM configuration

Set these values in `.env`:

- `LLM_PROVIDER`: `ollama` (default), `openai`, or `gemini`
- `OLLAMA_MODEL`: Ollama model name; defaults to `gemma4:31b`
- `OPENAI_API_KEY`: Required for `openai`; the app uses `gpt-4o-mini`
- `GEMINI_API_KEY`: Required for `gemini`; the app uses `gemini-flash-latest`

Values already set in the shell environment take precedence over `.env`.

## Project files

- `requirements.txt`: Python dependencies
- `st_english_tutor.py`: Streamlit UI, session state, navigation, and app behavior
- `prompts.py`: Grading and conversation prompts
- `.env_sample`: Safe configuration template

## Data storage

Submission history and chat history are stored in Streamlit session state. They are available while the current session is active and are not persisted after the session or server restarts.
