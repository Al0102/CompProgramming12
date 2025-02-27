import requests
import os

URL = "https://wttr.in/"

WWO_CODE = {
    "113": "Sunny","116": "PartlyCloudy","119": "Cloudy","122": "VeryCloudy","143": "Fog","176": "LightShowers","179": "LightSleetShowers","182": "LightSleet","185": "LightSleet","200": "ThunderyShowers","227": "LightSnow","230": "HeavySnow","248": "Fog","260": "Fog","263": "LightShowers","266": "LightRain","281": "LightSleet","284": "LightSleet","293": "LightRain","296": "LightRain","299": "HeavyShowers","302": "HeavyRain","305": "HeavyShowers","308": "HeavyRain","311": "LightSleet","314": "LightSleet","317": "LightSleet","320": "LightSnow","323": "LightSnowShowers","326": "LightSnowShowers","329": "HeavySnow","332": "HeavySnow","335": "HeavySnowShowers","338": "HeavySnow","350": "LightSleet","353": "LightShowers","356": "HeavyShowers","359": "HeavyRain","362": "LightSleetShowers","365": "LightSleetShowers","368": "LightSnowShowers","371": "HeavySnowShowers","374": "LightSleetShowers","377": "LightSleet","386": "ThunderyShowers","389": "ThunderyHeavyRain","392": "ThunderySnowShowers","395": "HeavySnowShowers",
}

WEATHER_SYMBOL = {
    "Unknown": "\033[33m✨","Cloudy": "☁️","Fog": "🌫","HeavyRain": "\033[34m🌧","HeavyShowers": "\033[34m🌧","HeavySnow": "❄️","HeavySnowShowers": "❄️","LightRain": "\033[34m🌦","LightShowers": "\033[34m🌦","LightSleet": "🌧","LightSleetShowers": "🌧","LightSnow": "🌨","LightSnowShowers": "🌨","PartlyCloudy": "⛅️","Sunny": "\033[33m☀️","ThunderyHeavyRain": "\033[33m🌩","ThunderyShowers": "\033[33m⛈","ThunderySnowShowers": "\033[33m⛈","VeryCloudy": "☁️",
}

def GET_byLocation(location,params=""):
    response = requests.get(URL+location.replace(' ', '+')+params)
    
    if (status:=response.status_code) == 404:
        return 404
    
    return response

def print_current_conditions(location: str):
    if (data:=GET_byLocation(location,"?format=j1")) == 404:
        return 404
    
    data = data.json()["current_condition"][0]

    print("Temperature: {}°C {}°F".format(data["temp_C"],data["temp_F"]))
    code = data["weatherCode"]
    weather = WWO_CODE[code]
    if weather in WEATHER_SYMBOL:
        symbol = WEATHER_SYMBOL[weather]
    else:
        symbol = WEATHER_SYMBOL["Unknown"]
    print("Weather: It is {} {}\033[0m".format(weather,symbol))

def main():
    os.system("cls" if os.name == 'posix' else "clear")
    print("Current weather at your location:")
    print_current_conditions("")
    print()
    while (choice:=input("(Current) weather by location\n(Forecast) by location\n(Quit)\n\n> ").lower()) != "quit":
        if choice not in ("current", "forecast"):
            continue

        location = input("Your location (blank for your current location): ").strip()
        if choice == "current":
            if print_current_conditions(location) == 404:
                print("Invalid location")
            print()
        elif choice == "forecast":
            # Full forecast
            response = GET_byLocation(location, '?d')
            if response == 404:
                print("Invalid location")
            print(response.text)
            print()
    
if __name__ == "__main__":
    main()
