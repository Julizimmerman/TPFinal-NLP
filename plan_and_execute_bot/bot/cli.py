"""Tiny REPL so you can chat from the terminal."""
import asyncio
from .graph import build_chatbot_graph

chatbot = build_chatbot_graph()

async def chat():
    state = {}  # accumulates plan / past_steps / response
    while True:
        try:
            user = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break

        state["input"] = user
        state.setdefault("past_steps", [])

        state = await chatbot.ainvoke(state)
        print("Bot >", state["response"])
        state.pop("response", None)  # reset so graph knows to continue next turn

if __name__ == "__main__":
    asyncio.run(chat())
