from sarvamai import SarvamAI
import json,os

MODEL_CONTEXT_LIMIT = 8192  # Adjust based on your model's maximum context length
WARN_THRESHOLD = 0.8  # Warn when context reaches 80% of the limit



data_all = []
export_history = []
json_file_path = "history.json"

user_api = input("Enter API Key : ")
model_name = input("Enter Model Name : ")
temperature = float(input("Enter temperature : "))
top_p = float(input("Enter Top P : "))
max_token = int(input("Enter Maximum Tokens : "))

def estimate_tokens(text: str) -> int:
    """Rough estimation of token count (~4 characters per token)."""
    return max(1, len(text) // 4)

if temperature >= 0 or temperature <=1:
    temp = temperature
else:
    print("Please Enter Valid Temperature between 0 and 1")

if top_p>=0 or top_p <=1:
    top__p = top_p
else:
    print("Please Enter Valid Top P between 0 and 1")

if max_token <= 500:
    max__token = max_token
else:
    print("Enter Tokens Less than 500 ")


client = SarvamAI(
    api_subscription_key= user_api
)

while True:
    user_input = input("You : ")
    
    if not user_input:
            continue
    if user_input.lower() in ["bye", "exit", "quit"]:
            print(" Nice to Meet You, Goodbye!")
            break
    
    else :
        response_list = [{"role": "user", "content": user_input}]
        total_tokens_used = estimate_tokens(user_input)
        
       
        
        current_context_tokens = sum(estimate_tokens(m["content"]) for m in response_list)

        if current_context_tokens >= (MODEL_CONTEXT_LIMIT * WARN_THRESHOLD):
            print(f"\n[WARNING] Approaching model context limit! ({current_context_tokens}/{MODEL_CONTEXT_LIMIT} tokens used)")


        response = client.chat.completions(
            model=model_name,
            messages= response_list,
            temperature=temp,
            top_p = top__p,
            max_tokens = max__token
        )

        
        response_all = response.choices[0].message.content

        

        response_list.append({"role": "Assistant", "content":response_all})

        prompt_tokens = getattr(response.usage, "prompt_tokens", current_context_tokens)
        completion_tokens = getattr(response.usage, "completion_tokens", estimate_tokens(response_all))
        turn_tokens = prompt_tokens + completion_tokens
        total_tokens_used += turn_tokens

        export_history = {
            "You":user_input,
            "LLM":response_all,
            "context_tokens": prompt_tokens,
            "response_tokens": completion_tokens,
            "Details":{
                "Model Name":response.model,
                "Temperature":temp,
                "Top P":top__p,
                "Maximum Tokens":max__token
            }
        }

        output_file = "history.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump({
                "system_prompt": response_all,
                "full_chat_history": response_list,
                "interactions": export_history
            }, f, indent=4)

        data_all.append(export_history)

        with open(json_file_path, "w", encoding="utf-8") as f:
            json.dump(data_all, f, indent=4, ensure_ascii=False)
                
        print("LLM : ",response_all)
        print("Model Name : ", response.model)     
        print("Temperature: ", temp)
        print("Top P : ",top__p)
        print("Maximum Tokens : ", max__token)
        print(f"Total Messages Exchanged: {len(response_list) - 1}")  # Excludes system prompt
        print(f"Current Context Size : {prompt_tokens} tokens")
        print(f"Total Session Tokens    : {total_tokens_used} tokens")

