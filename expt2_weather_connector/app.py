"""Expt 2 - Streamlit UI that makes the LLM <-> MCP tool interaction visible.

Run:  streamlit run app.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

load_dotenv()
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
SERVER = Path(__file__).parent / "server.py"

SYSTEM = (
    "You are a weather dashboard assistant. When the user asks about weather, first write ONE "
    "short sentence saying what you are going to do, then call get_current_weather with the "
    "location. After the tool result, give a friendly 2-3 sentence summary with a practical tip "
    "(for example whether to carry an umbrella). If the tool returns an ERROR, explain it simply."
)


async def run_agent(question: str, show) -> str:
    """Run one question through LLM + MCP. `show(kind, text)` displays each step live."""
    llm = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])
    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            llm_tools = [
                {"type": "function",
                 "function": {"name": t.name, "description": t.description or "",
                              "parameters": t.inputSchema}}
                for t in tools
            ]
            messages = [
                {"role": "system", "content": SYSTEM},
                {"role": "user", "content": question},
            ]
            while True:
                resp = llm.chat.completions.create(
                    model=MODEL, messages=messages, tools=llm_tools,
                    tool_choice="auto", max_tokens=1000,
                )
                msg = resp.choices[0].message
                if not msg.tool_calls:
                    return msg.content or ""

                if msg.content:
                    show("thought", msg.content)
                messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": [
                        {"id": tc.id, "type": "function",
                         "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                        for tc in msg.tool_calls
                    ],
                })
                for tc in msg.tool_calls:
                    args = json.loads(tc.function.arguments or "{}")
                    show("call", f"{tc.function.name}({args})")
                    result = await session.call_tool(tc.function.name, args)
                    out = "\n".join(c.text for c in result.content if c.type == "text")
                    show("result", out)
                    messages.append({"role": "tool", "tool_call_id": tc.id, "content": out})


st.set_page_config(page_title="Weather Data Dashboard", page_icon="\u26c5")
st.title("Weather Data Dashboard (MCP)")
st.caption("Ask about the weather. You will see the LLM decide to call the tool, then the final answer.")

if "history" not in st.session_state:
    st.session_state.history = []

for item in st.session_state.history:
    with st.chat_message(item["role"]):
        st.markdown(item["text"])

question = st.chat_input("e.g. What's the weather in Tokyo?")
if question:
    st.session_state.history.append({"role": "user", "text": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.status("Thinking...", expanded=True) as status:
            def show(kind: str, text: str) -> None:
                if kind == "thought":
                    st.markdown(f"**LLM thought:** {text}")
                elif kind == "call":
                    st.markdown("**Tool call:**")
                    st.code(text, language="python")
                else:
                    st.markdown("**Tool result (from wttr.in):**")
                    st.code(text, language="text")

            try:
                answer = asyncio.run(run_agent(question, show))
                status.update(label="Done", state="complete", expanded=True)
            except Exception as e:  # noqa: BLE001
                answer = f"Something went wrong: {e}"
                status.update(label="Error", state="error")
        st.markdown(answer)
    st.session_state.history.append({"role": "assistant", "text": answer})
