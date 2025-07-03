import requests
import json
import re

def get_weather(city):
    api_key = "c09acf824c95a28f5c88ae06991d1699"
    
    url = (f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric")
    
    try:
        response = requests.get(url)
        data = response.json()
        
        if data["cod"] != 200:
            speak("Sorry, I couldn't find the weather for that city.")
            return
        
        temp = data["main"]["temp"]
        weather = data["weather"][0]["description"]
        city_name = data["name"]
        speak(f"The current weather in {city_name} is {weather} with a temperature of {temp} ℃.")
    
    except Exception as e:
        speak("There was an error fetching the weather data.")
        print(f"[Weather Error]: {e}")
        
        
match = re.search(r"weather in (.+)", input_text)
if match:
    city = match.group(1)
    get_weather(city)
else:
    speak("Please specify a city. For example say 'Weather in Delhi'.")