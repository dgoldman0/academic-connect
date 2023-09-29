import openai
from datetime import datetime, timezone

# Evaluate a user's question.
def evaluate_question(question):
    with open('info/directory.md', 'r') as file:
        directory = file.read()    
        # Check if the question is appropriate.
        while True:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Specify the GPT-4 model
                max_tokens = 15,
                messages=[
                    {"role": "system", "content": "You are a academic communication assistant, answering questions and helping people connect with the academic community."},
                    {"role": "system", "content": "Check if the user's question is abusive. Only flag clearly abusive content. An abusive question appears INTENTIONALLY harmful or misleading. A question is only abusive if it is bigoted or if it spreads common pseudoscience, or conspiracy theories, such as science denial, antivax rhetoric, creationism, flat Earther rhetoric, etc. Respond only with abusive or sincere, by itself, with no other characters. Nothing more."},
                    {"role": "user", "content": f"Is the following question abusive or sincere: {question}."}
                ])
            response = response['choices'][0]['message']['content'].lower().strip()
            if response == "abusive" or response == "sincere":
                break
        sincere = response == "sincere"
        print(f"Sincerity: {sincere}")

        # If the system decided that the request was inappropriate, respond with the reason for the inappropriate nature of the request.
        while not sincere:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Specify the GPT-4 model
                max_tokens = 70,
                messages=[
                    {"role": "system", "content": f"You are a academic communication assistant (avoid using self references such as 'I'), answering questions and helping people connect with the academic community. You have deemed a user's question to problematic."},
                    {"role": "system", "content": "Assume the user is asking in earnest, and that they are not misunderstanding anything. Be constructive in your analysis, ask for clarification and suggest alternative questions and points to consider. Must be less than 300 characters."},
                    {"role": "user", "content": f"I have a question: {question}."}
                ])
            answer = response['choices'][0]['message']['content']
            if len(response) <= 300:
                # Check if the response might inflame the situation.
                response = openai.ChatCompletion.create(
                    model="gpt-4",  # Specify the GPT-4 model
                    max_tokens = 70,
                    messages=[
                        {"role": "system", "content": f"You are to determine whether an response to a question might make the user defensive."},
                        {"role": "user", "content": f"Question: {question}."},
                        {"role": "user", "content": f"Answer: {answer}"},
                        {"role": "user", "content": f"Would the provided answer likely make the person asking the question upset or otherwise become defensive? Answer with yes or no only."}
                    ])
                response = response['choices'][0]['message']['content'].strip().lower()
                if response == "no":
                    return answer

        # If the request is sincere, check if it can be answered by the system.
        while True:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Specify the GPT-4 model
                max_tokens = 15,
                messages=[
                    {"role": "system", "content": "You are a academic communication assistant, answering questions and helping people connect with the academic community. Your current task is to determine whether a question can be answered by the system itself or if expert knowledge is needed. Requests for latest information may be better answered by someone from the directory. Common theory questions, historical questions, etc. can be answered from general knowledge and do not need an expert."},
                    {"role": "user", "content": f"Question: {question}."},
                    {"role": "user", "content": f"Can this question be answered with known general knowledge or would someone from our academic directory be able to get a more useful answer?  Answer with general or expert, by itself."}
                ])
            response = response['choices'][0]['message']['content'].lower().strip()
            if response == "general" or response == "expert":
                break
        expert = response == "expert"
        print(f"Expertise: {expert}")

        # If the system has determined that expert knowledge is needed, find an expert in the network.
        while expert:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  # Specify the GPT-4 model
                max_tokens = 75,
                messages=[
                    {"role": "system", "content": f"You are a academic communication assistant, answering questions and helping people connect with the academic community. You have access to the following academic directory. The current time is {datetime.now(timezone.utc)}."},
                    {"role": "system", "content": directory},
                    {"role": "system", "content": "Do not attempt to answer the question. @ Tag in a specialist who can help with the question, if one is available. Your response must be under 300 characters total and must end in #AcademicConnect."},
                    {"role": "user", "content": f"I have a question: {question}."}
                ])
            response = response['choices'][0]['message']['content'].strip()
            if len(response) <= 300:
                return response
        
        # Otherwise answer the question using general knowledge.
        while True:
            response = openai.ChatCompletion.create(
                model="gpt-4",  # Specify the GPT-4 model
                max_tokens = 75,
                messages=[
                    {"role": "system", "content": f"You are an academic communication assistant, helping to answer various questions. You must answer in 300 characters or less."},
                    {"role": "user", "content": f"I have a question: {question}."}
                ])
            response = response['choices'][0]['message']['content'].strip()
            if len(response) <= 300:
                return response
