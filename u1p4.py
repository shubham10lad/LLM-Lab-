from sarvamai import SarvamAI
#import pandas as pd
#from dotenv import load_dotenv
import json



data_all = []
user_api = input("Enter API Key : ")
model_name = input("Enter Model Name : ")
temperature = float(input("Enter temperature : "))
top_p = float(input("Enter Top P : "))
max_token = int(input("Enter Maximum Tokens : "))


if temperature >= 0 or temperature <=1:
    temp = temperature
else:
    print("Please Enter Valid Temperature between 0 and 1")

if top_p>=0 or top_p <=1:
    top__p = top_p
else:
    print("Please Enter Valid Top P between 0 and 1")

#load_dotenv()
client = SarvamAI(
    api_subscription_key= user_api
)

while True:
    user_input = input("You : ")

    if user_input.lower() == "exit":
            print(" Nice to Meet You, Goodbye!")
            break
    else :
        response_list = [{"role": "user", "content": user_input}]

       

        response = client.chat.completions(
            model=model_name,
            messages= response_list,
            temperature=temp,
            top_p = top__p,
            max_tokens = max_token
        )

        
        response_all = response.choices[0].message.content
        
        
        response_list.append({"role": "Assistant", "content":response_all})
        
        add_data = {"You":user_input, "LLM":response_all,
                    "Details":{"Model Name":response.model,
                               "Temperature":temp,
                               "Top P":top__p,
                               "Maximum Tokens":max_token}}
        
        data_all.append(add_data)

        print(data_all)

        with open('data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)

        if not isinstance(data,list):
            data = [data]

        new_data = add_data
        data.append(new_data)
       
        with open("data.json", "w") as file:
            json.dump(data, file, indent=4)

        with open('data.json', 'r', encoding='utf-8') as file:
            data = json.load(file)


        
        print("LLM : ",response_all)
        print("Model Name : ", response.model)     
        print("Temperature: ", temp)
        print("Top P : ",top__p)
        print("Maximum Tokens : ", max_token)

