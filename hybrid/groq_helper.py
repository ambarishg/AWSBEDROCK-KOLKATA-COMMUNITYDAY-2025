from groq import Groq
import os

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

def create_prompt(context,query):
    header = "You are helpful assistant."
    return header + context + "\n\n" + query + "\n"


def generate_answer(conversation,model):
    chat_completion = client.chat.completions.create(
    messages=conversation,
    model=model,
)
    
    return (chat_completion.choices[0].message.content).strip()

def generate_reply_from_context(user_input, content, conversation,model="llama-3.3-70b-versatile"):
    prompt = create_prompt(content,user_input)            
    conversation.append({"role": "assistant", "content": prompt})
    conversation.append({"role": "user", "content": user_input})
    reply = generate_answer(conversation,model)
    return reply