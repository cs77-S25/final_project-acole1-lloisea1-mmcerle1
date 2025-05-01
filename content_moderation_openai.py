from openai import OpenAI
import requests
import os
from dotenv import load_dotenv
load_dotenv()  # take environment variables
#with open('api_key.txt', 'r') as file:
#    openai_apikey = file.read().strip()

#os.environ['OPENAI_API_KEY'] = openai_apikey

client = OpenAI()
 
def moderate_text(input_text):
    openai_apikey = os.getenv("OPENAI_API_KEY")
    print("in moderate text")
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {openai_apikey}',
    }
    data = {'input': input_text}
    response = client.moderations.create(
        model="omni-moderation-latest",
        input= input_text,
    )
    result = response.json()

    print(result)

    print("Result", result[len(result)-5])

    if result[len(result)-5] == "u":
        print('Content blocked: Violates usage policies.')
        return True
    else:
        print('Content allowed.')
        return False
