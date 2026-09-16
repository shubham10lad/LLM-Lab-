import asyncio
import csv
import json
import os
import re
import time
from sarvamai import AsyncSarvamAI

INPUT_CSV_PATH = "prompts.csv"
OUTPUT_FILE_PATH = "responsible_ai_batch_results.json"

COST_PER_1K_INPUT_TOKENS = 0.0015
COST_PER_1K_OUTPUT_TOKENS = 0.0020

DELAY_BETWEEN_REQUESTS = 1.0
MAX_RETRIES = 3
INITIAL_BACKOFF = 2.0

RESTRICTED_PROMPT_KEYWORDS = [
    "hack", "exploit", "malware", "virus", "bypass", "illegal", "kill",
    "weapon", "bomb", "terror", "suicide", "self-harm", "steal", "fraud"
]

OFFENSIVE_KEYWORDS = [
    "slur", "hate", "idiot", "stupid", "abuse", "harass"
]

HARMFUL_INSTRUCTION_KEYWORDS = [
    "how to make a bomb", "how to hack", "create malware", "bypass password",
    "ddos attack", "synthesize dangerous poison"
]

UNSAFE_RECOMMENDATION_KEYWORDS = [
    "guaranteed 100% profit", "stop taking your prescription",
    "drink bleach", "cure cancer with juice", "guaranteed return"
]

PII_PATTERNS = {
    "Email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
    "Phone Number": r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b",
    "Social Security / National ID": r"\b\d{3}-\d{2}-\d{4}\b",
    "Credit Card": r"\b(?:\d{4}[-\s]?){3}\d{4}\b"
}


def evaluate_prompt_safety(prompt: str) -> dict:
    """Checks prompt validity, empty status, and sensitive content prior to sending to LLM."""
    stripped_prompt = prompt.strip()
    
    if not stripped_prompt:
        return {
            "is_valid": False,
            "status": "Blocked",
            "reasons": ["Prompt is empty or contains only whitespace."]
        }

    warnings = []
    lowered = stripped_prompt.lower()
    
    for word in RESTRICTED_PROMPT_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', lowered):
            warnings.append(f"Contains sensitive or restricted keyword: '{word}'")

    if warnings:
        return {
            "is_valid": True,  # Send with warning flag
            "status": "Review Required",
            "reasons": warnings
        }

    return {
        "is_valid": True,
        "status": "Safe",
        "reasons": []
    }


def analyze_response_safety(response_text: str) -> dict:
    """Analyzes LLM generated text for PII, harmful instructions, offensive content, and unsafe advice."""
    if not response_text:
        return {"status": "N/A", "reasons": []}

    reasons = []
    lowered = response_text.lower()

    for pii_type, pattern in PII_PATTERNS.items():
        if re.search(pattern, response_text):
            reasons.append(f"Detected potential PII ({pii_type}).")

    for term in HARMFUL_INSTRUCTION_KEYWORDS:
        if term in lowered:
            reasons.append(f"Detected potential harmful instruction: '{term}'")

    for word in OFFENSIVE_KEYWORDS:
        if re.search(r'\b' + re.escape(word) + r'\b', lowered):
            reasons.append(f"Detected potentially offensive language: '{word}'")

    for recommendation in UNSAFE_RECOMMENDATION_KEYWORDS:
        if recommendation in lowered:
            reasons.append(f"Detected unsafe recommendation: '{recommendation}'")

    if reasons:
        return {"status": "Review Required", "reasons": reasons}
    
    return {"status": "Safe", "reasons": []}

def estimate_tokens(text: str) -> int:
    """Rough estimation of token count (~4 characters per token)."""
    return max(1, len(text) // 4) if text else 0

def calculate_cost(input_tokens: int, output_tokens: int) -> float:
    """Calculates estimated API cost based on token counts."""
    input_cost = (input_tokens / 1000.0) * COST_PER_1K_INPUT_TOKENS
    output_cost = (output_tokens / 1000.0) * COST_PER_1K_OUTPUT_TOKENS
    return input_cost + output_cost

def read_prompts_from_csv(file_path: str):
    """Reads prompts from a CSV file."""
    prompts = []
    if not os.path.exists(file_path):
        print(f"[Error] CSV file '{file_path}' not found.")
        return prompts

    with open(file_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames and "prompt" in reader.fieldnames:
            for row in reader:
                prompts.append(row["prompt"])
        else:
            f.seek(0)
            raw_reader = csv.reader(f)
            for row in raw_reader:
                if row:
                    prompts.append(row[0])
    return prompts


async def send_prompt_with_retry(client, model_name, prompt, temp, top_p, max_tokens):

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
            await asyncio.sleep(backoff)
            backoff *= 2

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

    interactions = []
    total_prompts_submitted = len(prompts)
    blocked_prompts_count = 0
    warnings_generated_count = 0
    total_response_time = 0.0
    successful_llm_calls = 0
    total_input_tokens = 0
    total_output_tokens = 0
    total_cost = 0.0

    print(f"Starting Responsible AI Batch Execution ({total_prompts_submitted} Prompts)")

    for idx, raw_prompt in enumerate(prompts, 1):
        print(f"[Prompt {idx}/{total_prompts_submitted}]")
        print(f"Input Text: \"{raw_prompt[:60]}...\"")

        # Step 1: Pre-generation Safety Check
        prompt_safety = evaluate_prompt_safety(raw_prompt)
        prompt_status = prompt_safety["status"]
        prompt_reasons = prompt_safety["reasons"]

        if prompt_status == "Review Required":
            warnings_generated_count += 1
            print(f"[Prompt Safety Warning]: {', '.join(prompt_reasons)}")
        elif prompt_status == "Blocked":
            blocked_prompts_count += 1
            print(f"[Prompt Blocked]: {', '.join(prompt_reasons)}")
            
            interactions.append({
                "id": idx,
                "prompt": raw_prompt,
                "execution_status": "Blocked",
                "safety_report": {
                    "prompt_status": prompt_status,
                    "response_status": "N/A",
                    "reasons": prompt_reasons
                },
                "response": None,
                "response_time_seconds": 0.0,
                "estimated_cost_usd": 0.0
            })
            continue

        prompt_tokens = estimate_tokens(raw_prompt)
        success, response_text, response_time = await send_prompt_with_retry(
            client, model_name, raw_prompt, temp, top_p, max_tokens
        )

        if not success:
            print(f" [Execution Failed]: {response_text}")
            interactions.append({
                "id": idx,
                "prompt": raw_prompt,
                "execution_status": "Failed",
                "safety_report": {
                    "prompt_status": prompt_status,
                    "response_status": "Error",
                    "reasons": [response_text]
                },
                "response": None,
                "response_time_seconds": 0.0,
                "estimated_cost_usd": 0.0
            })
            continue

        # Step 3: Post-generation Safety Analysis
        response_safety = analyze_response_safety(response_text)
        response_status = response_safety["status"]
        response_reasons = response_safety["reasons"]

        if response_status == "Review Required":
            warnings_generated_count += 1
            print(f"[Response Safety Warning]: {', '.join(response_reasons)}")
        else:
            print(f"[Response Safe]")

        completion_tokens = estimate_tokens(response_text)
        cost = calculate_cost(prompt_tokens, completion_tokens)
        
        successful_llm_calls += 1
        total_response_time += response_time
        total_input_tokens += prompt_tokens
        total_output_tokens += completion_tokens
        total_cost += cost

        all_warnings = prompt_reasons + response_reasons
        interactions.append({
            "id": idx,
            "prompt": raw_prompt,
            "execution_status": "Completed",
            "safety_report": {
                "prompt_status": prompt_status,
                "response_status": response_status,
                "reasons": all_warnings if all_warnings else ["No issues detected."]
            },
            "response": response_text,
            "response_time_seconds": round(response_time, 3),
            "input_tokens": prompt_tokens,
            "output_tokens": completion_tokens,
            "estimated_cost_usd": round(cost, 6)
        })

        await asyncio.sleep(DELAY_BETWEEN_REQUESTS)

    avg_response_time = (total_response_time / successful_llm_calls) if successful_llm_calls > 0 else 0.0

    usage_report = {
        "number_of_prompts_submitted": total_prompts_submitted,
        "number_of_blocked_prompts": blocked_prompts_count,
        "number_of_warnings_generated": warnings_generated_count,
        "average_response_time_seconds": round(avg_response_time, 3),
        "total_estimated_cost_usd": round(total_cost, 6),
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens
    }


    print("COMPLETE USAGE REPORT")
    print(f"Prompts Submitted : {usage_report['number_of_prompts_submitted']}")
    print(f"Blocked Prompts : {usage_report['number_of_blocked_prompts']}")
    print(f"Warnings Generated : {usage_report['number_of_warnings_generated']}")
    print(f"Average Response Time : {usage_report['average_response_time_seconds']}s")
    print(f"Total Estimated Cost : ${usage_report['total_estimated_cost_usd']:.6f}")

    output_package = {
        "usage_report": usage_report,
        "interaction_history": interactions
    }

    with open(OUTPUT_FILE_PATH, "w", encoding="utf-8") as f:
        json.dump(output_package, f, indent=4, ensure_ascii=False)

    print(f"\nInteraction history & safety report successfully saved to '{OUTPUT_FILE_PATH}'.")


if __name__ == "__main__":
    asyncio.run(main())