import os
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

api_key = "AQ.Ab8RN6IchY-eZdwtvubIKZvO_gQLTnEMamhh7pHvaBcWZA_qQA"
if not api_key:
    raise ValueError("GEMINI_API_KEY is missing from your .env file.")

# --- Inputs ---
Email_purpose = input("Enter the Email purpose: ")
Recipient_type = input("Enter the Recipient type: ")
Important_details = input("Enter the Important details: ")
Desired_tone = input("Enter the Desired tone: ")
to_name = input("Enter the to name: ")
from_name = input("Enter the from name: ")
start_date = input("Enter the start date: ")
end_date = input("Enter the end date: ")
return_date = input("Enter the return date: ")

# --- Models ---
chat_model = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=api_key,
    temperature=0.7,
)

output_parser = StrOutputParser()


prompt_template1 = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a professional Email Generator."),
        (
            "human",
            "Generate an email for purpose: '{email_purpose}', recipient type: '{recipient_type}', "
            "details: '{important_details}', tone: '{desired_tone}', to: '{to_name}', "
            "from: '{from_name}', start date: '{start_date}', end date: '{end_date}', return date: '{return_date}'.",
        ),
    ]
)

first_chain = prompt_template1 | chat_model | output_parser


prompt_template2 = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert Email Quality Assurance Specialist. Your job is to review draft emails and correct any formatting, structural, or clarity issues.",
        ),
        (
            "human",
            "Review the following draft email:\n\n{draft_email}\n\n"
            "Check for proper email structure (Subject Line, Salutation, Body Paragraphs, Call to Action/Closing, Sign-off). "
            "If the formatting is correct, output the polished email. If there are structural errors, correct them and return only the corrected, final email.",
        ),
    ]
)

second_chain = prompt_template2 | chat_model | output_parser


full_chain = (
    {
        "draft_email": first_chain
    }  
    | second_chain
)


try:
    print("\nGenerating and verifying email format...\n")
    final_email = full_chain.invoke(
        {
            "email_purpose": Email_purpose,
            "recipient_type": Recipient_type,
            "important_details": Important_details,
            "desired_tone": Desired_tone,
            "to_name": to_name,
            "from_name": from_name,
            "start_date": start_date,
            "end_date": end_date,
            "return_date": return_date,
        }
    )

    print(": FINAL VERIFIED EMAIL :")
    
    print(final_email)

except Exception as e:
    print(f"Error executing pipeline: {e}")