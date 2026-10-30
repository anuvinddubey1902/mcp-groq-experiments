# Expt 2: Data Dashboard Connector (MCP)

An MCP server exposing `get_current_weather(location)` (live data from wttr.in) and a Streamlit app that shows the LLM's tool-calling steps.

## Setup
```bash
python -m venv venv
venv\Scripts\activate        # Windows  (macOS/Linux: source venv/bin/activate)
pip install -r requirements.txt
copy .env.example .env       # macOS/Linux: cp .env.example .env  (then add your Groq API key)
```

## Run
```bash
streamlit run app.py
```
Try: `What's the weather in Tokyo?`, then an invalid place such as `weather in asdfghjkl` to see error handling.

## How it works
1. The user's question and the tool schema go to the LLM.
2. The LLM decides to call `get_current_weather` (shown in the UI as "Tool call").
3. The client runs the tool on the MCP server, which fetches wttr.in ("Tool result").
4. The result goes back to the LLM, which writes the final summary.
