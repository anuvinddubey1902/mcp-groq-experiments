# MCP Groq Experiments

Two Python experiments demonstrating Model Context Protocol (MCP)
integration with Groq LLMs.

## Experiment 1: Personal Assistant Memory Server

An MCP-based assistant that manages notes.

Features:
- save_note()
- search_notes()
- list_notes()
- update_note()
- delete_note()

Technologies:
- Python
- MCP
- Groq API
- JSON storage

## Experiment 2: Weather Data Dashboard Connector

An MCP-based weather assistant with a Streamlit interface.

Features:
- Retrieves current weather information.
- Uses Groq to interpret user questions.
- Automatically invokes the weather tool.
- Displays tool calls and results.
- Handles invalid locations.

Technologies:
- Python
- MCP
- Groq API
- Streamlit
- HTTPX
- wttr.in

## Project Structure

- expt1_memory_server/
- expt2_weather_connector/
- README.md
- EXECUTION.md

## Installation

Install dependencies:

pip install -r expt1_memory_server/requirements.txt

pip install -r expt2_weather_connector/requirements.txt

Configure your GROQ_API_KEY environment variable.

## Running Experiment 1

cd expt1_memory_server
python client.py

## Running Experiment 2

cd expt2_weather_connector
streamlit run app.py

## Execution Environment

Google Colab

## Original Repository

https://github.com/Xalibur1/mcp_groq

Original project attribution is retained.
