from openai import OpenAI
from dotenv import load_dotenv
import os

preresponce_id = None
def createTextResponse(input_message,personal_log):
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    GPTclient = OpenAI()

    rollfile = open('SubRolls.txt', 'r', encoding='utf-8')
    rolltext = rollfile.read()

    try:
        response = GPTclient.responses.create(
        model="gpt-4.1",
        instructions= f"日本語,口語調,100文字以内,{rolltext}\n{personal_log}",
        input=input_message,
        max_output_tokens=400,
        temperature=0.2,
        )

        rollfile.close()
    except Exception as e:
        print(f"APIエラー: {e}")
    
    return response.output_text