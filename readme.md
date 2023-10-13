Start from main: python main.py

Please create an .env file and insert your openai api key:
OPENAI_API_KEY=**USE YOUR KEY**
WEATHER_API_KEY=**USE YOUR KEY**

Tips:
https://www.youtube.com/watch?v=dgV4WFisK5Y
https://www.youtube.com/watch?v=0lOSvOoF2to

This is about how to use openai functions

This is the scenario: i want to ask GPT to provide me with some information regarding the weather in a specified city. Of course GPT cannot access "external" information, so we have openai functions.

First of all we subscribe (for free) to http://api.weatherapi.com
we receive a KEY that could be used to query the weatherapi api in the following way:
http://api.weatherapi.com/v1/current.json?key={weather_api_key}&q={city}&aqi=no

When we specify the "city" we are able to retrieve a json with a lot of information. In this example we are just interested in the "text" message containing a textual label regarding the weather; so once we receive the response:
weather_data = response.json()
weather_label = weather_data['current']['condition']['text']

The complete flow is therefore the following:

1. we ask the user to inser the city
2. we ask openai passing a new parameter:

completion = openai.ChatCompletion.create(
model="gpt-3.5-turbo-0613",
messages=messages,
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
],
#function_call={"name": "get_current_weather"},
function_call="auto"
)

instead of the usual model and messages

3. we parse the response that will be something like the following:

{
"id": "chatcmpl-89DRciGw45ZX07nvUeDnAq2UdmEPH",
"object": "chat.completion",
"created": 1697207324,
"model": "gpt-3.5-turbo-0613",
"choices": [
{
"index": 0,
"message": {
"role": "assistant",
"content": null,
"function_call": {
"name": "get_current_weather",
"arguments": "{\n \"city\": \"Velletri\"\n}"
}
},
"finish_reason": "function_call"
}
],
"usage": {
"prompt_tokens": 91,
"completion_tokens": 18,
"total_tokens": 109
}
}

4. once identified that openai has recognized that we want to use a function we perform the OUR FUNCTION, that will perform the call to weatherapi in order to obtain the correct REAL TIME info
5. once received the response we pass everything to GPT in order to get a "full answer"

{
"id": "chatcmpl-89E4spbTBF7ee43bMilU6wI2MHk65",
"object": "chat.completion",
"created": 1697209758,
"model": "gpt-3.5-turbo-0613",
"choices": [
{
"index": 0,
"message": {
"role": "assistant",
"content": "The current weather in Velletri is partly cloudy."
},
"finish_reason": "stop"
}
],
"usage": {
"prompt_tokens": 57,
"completion_tokens": 11,
"total_tokens": 68
}
}

BEWARE: it is necessary to maintain the "messages" updated in order to have a correst CHAT with openai

It is possible to use LangChain (as implemented in the related function) in order to "ease" the process
