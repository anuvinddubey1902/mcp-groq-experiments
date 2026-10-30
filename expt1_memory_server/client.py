"""Expt 1 - MCP client. An LLM (Groq, OpenAI-compatible API) decides whether to call
save_note / search_notes.

Run:  python client.py
"""
import asyncio
import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI

load_dotenv()
MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
SERVER = Path(__file__).parent / "server.py"

SYSTEM = (
    "You are a personal assistant with a memory. If the user tells you something to remember, "
    "call save_note with the content and 1-3 short lowercase tags. If the user asks about "
    "something they said earlier, call search_notes with the key words. Use list_notes, "
    "update_note or delete_note only when asked. After a tool result, answer briefly using it."
)


async def main() -> None:
    llm = OpenAI(api_key=os.environ["GROQ_API_KEY"], base_url="https://api.groq.com/openai/v1")
    params = StdioServerParameters(command=sys.executable, args=[str(SERVER)])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = (await session.list_tools()).tools
            llm_tools = [
                {
                    "type": "function",
                    "function": {
                        "name": t.name,
                        "description": t.description or "",
                        "parameters": t.inputSchema,
                    },
                }
                for t in tools
            ]
            print("Connected to MCP server. Tools:", ", ".join(t.name for t in tools))
            print("Type a message (or 'quit').\n")

            messages: list[dict] = [{"role": "system", "content": SYSTEM}]
            while True:
                user = input("You: ").strip()
                if user.lower() in {"quit", "exit"}:
                    break
                if not user:
                    continue
                messages.append({"role": "user", "content": user})

                while True:
                    resp = llm.chat.completions.create(
                        model=MODEL, messages=messages, tools=llm_tools,
                        tool_choice="auto", max_tokens=1000,
                    )
                    msg = resp.choices[0].message

                    if not msg.tool_calls:
                        messages.append({"role": "assistant", "content": msg.content or ""})
                        print(f"Assistant: {msg.content}\n")
                        break

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
                        print(f"  [LLM chose tool] {tc.function.name}({args})")
                        result = await session.call_tool(tc.function.name, args)
                        text = "\n".join(c.text for c in result.content if c.type == "text")
                        print(f"  [Tool result]    {text}")
                        messages.append({"role": "tool", "tool_call_id": tc.id, "content": text})


if __name__ == "__main__":
    asyncio.run(main())
