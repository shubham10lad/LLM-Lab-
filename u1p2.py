GPT = { 
    "Developer" : "OpenAI",
    "Open Source/ Proprictory" : "Proprietary",
    "Multimodal Support (Yes/No)"  : "Yes",
    "Typical Use Cases" : "Complex Problem Solving & Reasoning, Code Generation & Technical Debugging, Document & Image Analysis"
}

Claude = { 
    "Developer" : "Anthropic",
    "Open Source/ Proprictory" : "Proprietary",
    "Multimodal Support (Yes/No)"  : "Yes",
    "Typical Use Cases" : "Complex Cognitive Tasks & Reasoning, Visual Data Analysis, Software Development & Coding"
}

Gemini = { 
    "Developer" : "Google",
    "Open Source/ Proprictory" : "Proprietary",
    "Multimodal Support (Yes/No)"  : "Yes",
    "Typical Use Cases" : "Multimodal Search & Synthesis, Workspace Integration & Productivity, Complex Reasoning & Problem Solving"
}

Liama = { 
    "Developer" : "Meta",
    "Open Source/ Proprictory" : "Open Source",
    "Multimodal Support (Yes/No)"  : "Yes",
    "Typical Use Cases" : "On-Premise & Private AI Deployment, Domain-Specific Fine-Tuning, On-Device & Edge Computing"
}

Mistral = { 
    "Developer" : "Mistral AI",
    "Open Source/ Proprictory" : "Open-Source & Commercial Hybrid",
    "Multimodal Support (Yes/No)"  : "Yes",
    "Typical Use Cases" : "Self-Hosted & Edge Deployments, Code Generation & Development, Document Intelligence & Visual OCR"
}

user =  input("Enter Topic Number : ")
user_data = user.upper()

if user_data =="GPT" or user_data == "GPT 4":
    print(GPT)
elif user_data =="Claud" or user_data == "Claud 3":
    print(Claude)
elif user_data =="Gemini":
    print(Gemini)
elif user_data =="Liama" or user_data == "Liama 3":
    print(Liama)
elif user_data =="Mistral":
    print(Mistral)
else :
    print("Enter Valid Name ")