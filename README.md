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

3. Complete the setup for your selected provider.

#### Ollama

Install Ollama, start the Ollama service, and download the configured model. For the default configuration:

```bash
ollama pull gemma4:31b
```

If that model is too large for your computer, choose another installed Ollama model and set its name in `OLLAMA_MODEL`.

#### OpenAI

Set `LLM_PROVIDER=openai` and replace the placeholder value of `OPENAI_API_KEY` in `.env` with an API key from OpenAI. The app uses the `gpt-4o-mini` model.

#### Gemini

Set `LLM_PROVIDER=gemini` and replace the placeholder value of `GEMINI_API_KEY` in `.env` with an API key from Google AI Studio. The app uses the `gemini-flash-latest` model.

## Run the app

```bash
streamlit run st_english_tutor.py
```

Streamlit will print a local URL, usually `http://localhost:8501`.

## Environment variables

### `LLM_PROVIDER`

Selects the language model provider. Supported values are:

- `ollama`: Uses a local Ollama server. This is the default when the variable is not set.
- `openai`: Uses the OpenAI API and requires `OPENAI_API_KEY`.
- `gemini`: Uses the Google Gemini API and requires `GEMINI_API_KEY`.

The value loaded from `.env` is used when `LLM_PROVIDER` is not already set in the shell environment. To use Ollama, set:

```dotenv
LLM_PROVIDER=ollama
```

### `OLLAMA_MODEL`

The model name sent to Ollama when `LLM_PROVIDER=ollama`. The default is:

```dotenv
OLLAMA_MODEL=gemma4:31b
```

The model must be available in Ollama. Use `ollama list` to see downloaded models.

### `OPENAI_API_KEY`

Your OpenAI API key. This is used only when:

```dotenv
LLM_PROVIDER=openai
```

The app currently sends requests to the `gpt-4o-mini` model.

### `GEMINI_API_KEY`

Your Google Gemini API key. This is used only when:

```dotenv
LLM_PROVIDER=gemini
```

The app currently sends requests to the `gemini-flash-latest` model.

## Project files

- `requirements.txt`: Python dependencies
- `st_english_tutor.py`: Streamlit UI, session state, navigation, and app behavior
- `prompts.py`: Grading and conversation prompts
- `.env_sample`: Safe configuration template

## Data storage

Submission history and chat history are stored in Streamlit session state. They are available while the current session is active and are not persisted after the session or server restarts.
