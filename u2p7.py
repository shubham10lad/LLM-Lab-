import asyncio
import csv
import json
import os
import time
from sarvamai import AsyncSarvamAI

# Configurations & Cost Estimations
MODEL_CONTEXT_LIMIT = 8192
INPUT_CSV_PATH = "prompts.csv"
OUTPUT_FILE_PATH = "batch_results.json"  # Change to output.csv to export as CSV

# Adjust pricing per 1,000 tokens based on target model pricing
COST_PER_1K_INPUT_TOKENS = 0.0015
COST_PER_1K_OUTPUT_TOKENS = 0.0020


DELAY_BETWEEN_REQUESTS = 1.0  # Delay in seconds between calls
MAX_RETRIES = 3
INITIAL_BACKOFF = 2.0  # Base delay in seconds for exponential backoff


def estimate_tokens(text: str) -> int:
    """Rough estimation of token count (~4 characters per token)."""
    return max(1, len(text) // 4) if text else 0


def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculates estimated API cost based on token counts."""
    input_cost = (input_tokens / 1000.0) * COST_PER_1K_INPUT_TOKENS
    output_cost = (output_tokens / 1000.0) * COST_PER_1K_OUTPUT_TOKENS
    return input_cost + output_cost


def read_prompts_from_csv(file_path: str):
    """Reads prompts from a CSV file (expects column named 'prompt' or takes first column)."""
    prompts = []
    if not os.path.exists(file_path):
        print(f"[Error] CSV file '{file_path}' not found.")
        return prompts

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames and "prompt" in reader.fieldnames:
            for row in reader:
                if row["prompt"].strip():
                    prompts.append(row["prompt"].strip())
        else:
            # Fallback to reading raw lines if no header found
            f.seek(0)
            raw_reader = csv.reader(f)
            for row in raw_reader:
                if row and row[0].strip():
                    prompts.append(row[0].strip())
    return prompts


async def send_prompt_with_retry(client, model_name, prompt, temp, top_p, max_tokens):
    """Sends prompt to the API with retry logic and exponential backoff for rate limits."""
    messages = [{"role": "user", "content": prompt}]
    attempt = 0
    backoff = INITIAL_BACKOFF

    while attempt <= MAX_RETRIES:
        try:
            start_time = time.perf_counter()
            response = await client.chat.completions(
                model=model_name,
                messages=messages,
                temperature=temp,
                top_p=top_p,
                max_tokens=max_tokens,
                stream=False,
            )
            response_time = time.perf_counter() - start_time
            response_text = response.choices[0].message.content
            return True, response_text, response_time

        except Exception as e:
            attempt += 1
            if attempt > MAX_RETRIES:
                return False, str(e), 0.0
            
            print(f"   [API Error/Rate Limit] Retry {attempt}/{MAX_RETRIES} in {backoff}s... (Error: {e})")
            await asyncio.sleep(backoff)
            backoff *= 2  # Exponential backoff


async def main():
    user_api = input("Enter API Key: ").strip()
    model_name = input("Enter Model Name: ").strip()

    try:
        temp = float(input("Enter temperature (0-1) [0.7]: ") or 0.7)
    except ValueError:
        temp = 0.7

    try:
        top_p = float(input("Enter Top P (0-1) [1.0]: ") or 1.0)
    except ValueError:
        top_p = 1.0

    try:
        max_tokens = int(input("Enter Maximum Tokens (<=500) [100]: ") or 100)
    except ValueError:
        max_tokens = 100

    prompts = read_prompts_from_csv(INPUT_CSV_PATH)
    if not prompts:
        print("No prompts found to process. Exiting.")
        return

    client = AsyncSarvamAI(api_subscription_key=user_api)

    results = []
    successful_requests = 0
    failed_requests = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0

    print(f"\nStarting Batch Processing ({len(prompts)} prompts)\n")

    for idx, prompt in enumerate(prompts, 1):
        print(f"Processing Prompt [{idx}/{len(prompts)}]: \"{prompt[:40]}...\"")
        
        prompt_tokens = estimate_tokens(prompt)
        success, response_text, response_time = await send_prompt_with_retry(
            client, model_name, prompt, temp, top_p, max_tokens
        )

        if success:
            successful_requests += 1
            status = "Success"
            completion_tokens = estimate_tokens(response_text)
            cost = calculate_cost(prompt_tokens, completion_tokens)

            total_input_tokens += prompt_tokens
            total_output_tokens += completion_tokens
            total_cost += cost

            print(f" Status: SUCCESS | Time: {response_time:.2f}s | Est. Tokens: {prompt_tokens + completion_tokens} | Est. Cost: ${cost:.6f}")
        else:
            failed_requests += 1
            status = "Failed"
            completion_tokens = 0
            cost = 0.0
            print(f" Status: FAILED | Error: {response_text}")

        results.append({
            "id": idx,
            "prompt": prompt,
            "status": status,
            "response": response_text if success else None,
            "error": response_text if not success else None,
            "response_time_seconds": round(response_time, 3),
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "estimated_cost_usd": round(cost, 6)
        })

        # Rate-limiting delay between sequential calls
        await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    # --- Summary Report ---
    total_tokens_all = total_input_tokens + total_output_tokens

    print(": SUMMARY REPORT : ")
    print(f"Total Prompts Processed : {len(prompts)}")
    print(f"Successful Requests     : {successful_requests}")
    print(f"Failed Requests         : {failed_requests}")
    print(f"Total Input Tokens      : {total_input_tokens}")
    print(f"Total Output Tokens     : {total_output_tokens}")
    print(f"Total Estimated Tokens  : {total_tokens_all}")
    print(f"Total Estimated API Cost: ${total_cost:.6f}")

    # Exporting Results
    if OUTPUT_FILE_PATH.endswith(".json"):
        with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        print(f"Results successfully exported to JSON: {OUTPUT_FILE_PATH}")

    elif OUTPUT_FILE_PATH.endswith(".csv"):
        fieldnames = list(results[0].keys()) if results else []
        with open(OUTPUT_FILE_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"Results successfully exported to CSV: {OUTPUT_FILE_PATH}")


if __name__ == "__main__":
    asyncio.run(main())