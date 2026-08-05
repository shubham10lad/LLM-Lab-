from sarvamai import SarvamAI
from dotenv import load_dotenv
import time

import os 

load_dotenv()
client = SarvamAI(
    api_subscription_key= os.getenv("SARVAN_API")
)

while True:
    user_input = input("You : ")

    if user_input.lower() == "exit":
            print(" Nice to Meet You, Goodbye!")
            break
    else :
        response_list = [{"role": "user", "content": user_input}]

        start_time = time.perf_counter()

        response = client.chat.completions(
            model="sarvam-105b",
            messages= response_list
        )
        end_time = time.perf_counter()
        total_time = end_time - start_time

        response_all = response.choices[0].message.content
        response_list.append({"role": "assistant", "content":response_all})

        
        print("LLM : ",response_all)
        print("Len of Response : ", len(response_all))
        total_words =  len(response_all.split())
        print("Total Word of Response : ", total_words)
        print("Time of Response : ", total_time)
        print("Model Name : ", response.model)
        if total_words <= 50:
            print("Response is Short")
        elif total_words <= 50 and total_words >= 150:
            print("Response is Medium")
        else:
            print("Response is Medium")
        


# user_input = input("You : ")
# response_list.append({"role": "assistant", "content":user_input})


# response_2 = client.chat.completions(
#     model="sarvam-105b",
#     messages= response_list
# )

# response_all = response_2.choices[0].message.content
# print(response_all)
