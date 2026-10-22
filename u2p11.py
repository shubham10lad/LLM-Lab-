
import ollama

MODEL_NAME = "llama3.2:3b"

print(" SUBJECT-BASED QUESTION ANSWERING SYSTEM")
print(" Using Ollama and Python")
print("=" * 50)

print("\nAvailable Subjects:")
print("1. Python Programming")
print("2. Operating Systems")
print("3. Computer Networks")

subject_choice = input("\nSelect subject (1-3): ")

subjects = {
    "1": "Python Programming",
    "2": "Operating Systems",
    "3": "Computer Networks"
}

if subject_choice not in subjects:
    print("Invalid subject selection.")
    exit()

subject = subjects[subject_choice]

print("\nSelected Subject:", subject)
print("Ask your questions below.")
print("Type 'exit' to close the application.\n")

while True:
    question = input("Enter your question: ").strip()

    if question.lower() == "exit":
        print("Thank you for using the system!")
        break

    if not question:
        print("Please enter a question.")
        continue

    try:
        response = ollama.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        f"You are a helpful teacher specializing in "
                        f"{subject}. Answer questions related to "
                        f"{subject} in simple English. Give clear "
                        f"explanations and examples when appropriate. "
                        f"If a question is unrelated to the subject, "
                        f"politely ask the student to ask a "
                        f"{subject}-related question."
                    )
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )

        answer = response["message"]["content"]

        print("\nAnswer:")
        print(answer)

    except ollama.ResponseError as error:
        print("Ollama model error:", error)

    except Exception as error:
        print("Connection error:", error)
        print("Check that Ollama is running and the model is installed.")
