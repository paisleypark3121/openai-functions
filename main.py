import os

from dotenv import load_dotenv
load_dotenv()

weather_api_key=os.getenv("WEATHER_API_KEY")
openai_api_key=os.getenv("OPENAI_API_KEY")

import requests
def get_weather(city,weather_api_key):
    url = f"http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&aqi=no"

    try:
        response = requests.get(url)
        if response.status_code == 200:
            weather_data = response.json()
            return weather_data['current']['condition']['text']
        else:
            print(f"Error: {response.status_code}")
            return None

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

import openai
import json

functions=[
    {
        "name": "get_current_weather",
        "description": "Get the current weather in a given location",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA",
                },
                "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]},
            },
            "required": ["location"],
        },
    }
]

def standard_function():

    #print("STANDARD")

    messages = [{
        'role': 'system',
        'content': 'Perform function requests for the user',
    }];

    city=input("What's the name of the city? ")
    user_message = {
        'role': 'user',
        'content': f'What\'s the weather like in {city}?',
    }
    messages.append(user_message)

    openai.api_key = openai_api_key
    completion = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=messages,
        functions=functions,
        #function_call={"name": "get_current_weather"},
        function_call="auto"
    )

    #print(completion)
    # {
    #   "id": "chatcmpl-89DRciGw45ZX07nvUeDnAq2UdmEPH",
    #   "object": "chat.completion",
    #   "created": 1697207324,
    #   "model": "gpt-3.5-turbo-0613",
    #   "choices": [
    #     {
    #       "index": 0,
    #       "message": {
    #         "role": "assistant",
    #         "content": null,
    #         "function_call": {
    #           "name": "get_current_weather",
    #           "arguments": "{\n  \"city\": \"Velletri\"\n}"
    #         }
    #       },
    #       "finish_reason": "function_call"
    #     }
    #   ],
    #   "usage": {
    #     "prompt_tokens": 91,
    #     "completion_tokens": 18,
    #     "total_tokens": 109
    #   }
    # }

    if completion.choices[0].finish_reason == "function_call" and completion.choices[0].message.function_call.name == "get_current_weather":
        
        args=json.loads(completion.choices[0].message.function_call.arguments)
        city=args.get("city")
        print(city)
        response=get_weather(city,weather_api_key)

        messages.append(completion.choices[0].message)
        function_message = {
            'role': 'function',
            'name': completion.choices[0].message.function_call.name,
            'content': response
        }
        messages.append(function_message)
        
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",
            messages=messages)
        
        #print(completion)
        # {
        #     "id": "chatcmpl-89E4spbTBF7ee43bMilU6wI2MHk65",
        #     "object": "chat.completion",
        #     "created": 1697209758,
        #     "model": "gpt-3.5-turbo-0613",
        #     "choices": [
        #         {
        #         "index": 0,
        #         "message": {
        #             "role": "assistant",
        #             "content": "The current weather in Velletri is partly cloudy."
        #         },
        #         "finish_reason": "stop"
        #         }
        #     ],
        #     "usage": {
        #         "prompt_tokens": 57,
        #         "completion_tokens": 11,
        #         "total_tokens": 68
        #     }
        # }


from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, AIMessage, ChatMessage
def langchain_function():
    #print("LANGCHAIN")

    llm=ChatOpenAI(model="gpt-3.5-turbo-0613")
    # message=llm.predict_messages(
    #     [HumanMessage(content="what is the capital of France?")],
    #     functions=functions
    # )
    #print(message)
    #content='The capital of France is Paris.' additional_kwargs={} example=False

    query="what is the weather like in Velletri?"
    message=llm.predict_messages(
        [HumanMessage(content=query)],
        functions=functions
    )
    #print(message)
    #content='' additional_kwargs={'function_call': {'name': 'get_current_weather', 'arguments': '{\n  "city": "Velletri"\n}'}} example=False

    city=json.loads(message.additional_kwargs["function_call"]["arguments"]).get("city")
    weather_response=get_weather(city,weather_api_key)

    response=llm.predict_messages(
        [
            HumanMessage(content=query),
            AIMessage(content=str(message.additional_kwargs)),
            ChatMessage(
                role="function",
                additional_kwargs={
                    "name":message.additional_kwargs["function_call"]["name"]
                },
                content=weather_response
            )
        ],
        functions=functions
    )
    print(response)
    #content='The weather in Velletri is currently partly cloudy.' additional_kwargs={} example=False

#standard_function()
langchain_function()