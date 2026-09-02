import asyncio
import json
import os
import sys
import time
from sarvamai import AsyncSarvamAI

MODEL_CONTEXT_LIMIT = 8192
WARN_THRESHOLD = 0.8
JSON_FILE_PATH = "history.json"


def estimate_tokens(text: str) -> int:
    """Rough estimation of token count (~4 characters per token)."""
    return max(1, len(text) // 4)


def load_history():
    if os.path.exists(JSON_FILE_PATH):
        try:
            with open(JSON_FILE_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []
    return []


async def main():
    data_all = load_history()
    conversation_history = []

    user_api = input("Enter API Key : ").strip()
    model_name = input("Enter Model Name : ").strip()

    try:
        temp = float(input("Enter temperature (0-1) : "))
        if not (0 <= temp <= 1):
            temp = 0.7
            print("Invalid range. Defaulting temperature to 0.7")
    except ValueError:
        temp = 0.7

    try:
        top__p = float(input("Enter Top P (0-1) : "))
        if not (0 <= top__p <= 1):
            top__p = 1.0
            print("Invalid range. Defaulting Top P to 1.0")
    except ValueError:
        top__p = 1.0

    try:
        max__token = int(input("Enter Maximum Tokens (<=500) : "))
        if max__token > 500:
            max__token = 500
            print("Token limit set to maximum threshold of 500.")
    except ValueError:
        max__token = 100

    client = AsyncSarvamAI(api_subscription_key=user_api)

    print("\nSelect Response Mode:")
    print("1. Streaming Response")
    print("2. Normal API Response")
    mode_choice = input("Choice (1/2): ").strip()
    is_stream = mode_choice != "2"

    print("\n--- Assistant Ready ---\n")

    while True:
        user_input = await asyncio.to_thread(input, "\nYou : ")
        user_input = user_input.strip()

        if not user_input:
            continue
        if user_input.lower() in ["bye", "exit", "quit"]:
            print("Nice to Meet You, Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_input})

        current_context_tokens = sum(
            estimate_tokens(m["content"]) for m in conversation_history
        )
        if current_context_tokens >= (MODEL_CONTEXT_LIMIT * WARN_THRESHOLD):
            print(
                f"\n[WARNING] Approaching context limit! ({current_context_tokens}/{MODEL_CONTEXT_LIMIT} tokens used)"
            )

        start_time = time.perf_counter()
        first_token_time = None
        response_all = ""
        chunk_count = 0

        try:
            if is_stream:
                print("LLM : ", end="", flush=True)

                # અહીંથી .create કાઢી નાખ્યું છે
                stream = await client.chat.completions(
                    model=model_name,
                    messages=conversation_history,
                    temperature=temp,
                    top_p=top__p,
                    max_tokens=max__token,
                    stream=True,
                )

                async for chunk in stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta_content = getattr(
                            chunk.choices[0].delta, "content", ""
                        )
                        if delta_content:
                            if first_token_time is None:
                                first_token_time = (
                                    time.perf_counter() - start_time
                                )

                            chunk_count += 1
                            response_all += delta_content
                            print(delta_content, end="", flush=True)

                print()

            else:
                # અહીંથી પણ .create કાઢી નાખ્યું છે
                response = await client.chat.completions(
                    model=model_name,
                    messages=conversation_history,
                    temperature=temp,
                    top_p=top__p,
                    max_tokens=max__token,
                    stream=False,
                )
                first_token_time = time.perf_counter() - start_time
                response_all = response.choices[0].message.content
                print(f"LLM : {response_all}")

        except (asyncio.CancelledError, KeyboardInterrupt):
            print("\n[Request cancelled or interrupted by user]")
            conversation_history.pop()
            continue
        except Exception as e:
            print(
                f"\n[Network/API Error]: {e}. Partial output retained where applicable."
            )
            if not response_all:
                conversation_history.pop()
                continue

        total_response_time = time.perf_counter() - start_time

        conversation_history.append(
            {"role": "assistant", "content": response_all}
        )

        prompt_tokens = current_context_tokens
        completion_tokens = estimate_tokens(response_all)

        export_history = {
            "You": user_input,
            "LLM": response_all,
            "context_tokens": prompt_tokens,
            "response_tokens": completion_tokens,
            "Details": {
                "Model Name": model_name,
                "Temperature": temp,
                "Top P": top__p,
                "Maximum Tokens": max__token,
                "Time To First Token": f"{first_token_time:.3f}s"
                if first_token_time
                else "N/A",
                "Total Response Time": f"{total_response_time:.3f}s",
                "Stream Chunks": chunk_count if is_stream else "N/A",
            },
        }

        data_all.append(export_history)
        with open(JSON_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data_all, f, indent=4, ensure_ascii=False)

        print("\n--- Response Performance Metrics ---")
        print(
            f"Time to First Token : {first_token_time:.3f}s"
            if first_token_time
            else "Time to First Token : N/A"
        )
        print(f"Total Response Time : {total_response_time:.3f}s")
        if is_stream:
            print(f"Stream Chunks Count : {chunk_count}")
        print(f"Context Tokens Used : {prompt_tokens}")
        print(f"Completion Tokens   : {completion_tokens}")


if __name__ == "__main__":
    asyncio.run(main())