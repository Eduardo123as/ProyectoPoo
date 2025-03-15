from flask import Flask, render_template, request, send_file
import requests
from dotenv import load_dotenv
import os
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from io import BytesIO
import time
import math  # Se utiliza para calcular los rayos del sol

load_dotenv()

app = Flask(__name__)
api_key = os.getenv('API_KEY')

def get_weather(api_key, city):
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': city,
        'appid': api_key,
        'units': 'metric'
    }
    response = requests.get(base_url, params=params)
    return response.json()

def draw_weather(weather_data):
    city = weather_data['name']
    temp = weather_data['main']['temp']
    weather = weather_data['weather'][0]['main'].lower()
    description = weather_data['weather'][0]['description']

    with Image(width=600, height=400, background=Color('#87CEEB')) as img:
        with Drawing() as draw:
            # Dibuja el suelo (pasto)
            draw.fill_color = Color('#32CD32')
            draw.rectangle(left=0, top=300, width=600, height=100)
            
            if 'clear' in weather:
                # Dibuja un sol con rayos para un día despejado
                draw.fill_color = Color('#FFD700')
                # Sol: círculo con centro en (500,100) y radio 50
                draw.circle((500, 100), (550, 100))
                # Rayos del sol
                draw.stroke_color = Color('#FFD700')
                draw.stroke_width = 4
                for angle in range(0, 360, 30):
                    rad = math.radians(angle)
                    x_end = 500 + math.cos(rad) * 70
                    y_end = 100 + math.sin(rad) * 70
                    draw.line((500, 100), (x_end, y_end))
            elif 'cloud' in weather:
                # Dibuja nubes con elipses superpuestas para mayor suavidad
                draw.fill_color = Color('white')
                draw.ellipse((150, 100), (60, 40))
                draw.ellipse((220, 90), (70, 50))
                draw.ellipse((290, 100), (60, 40))
            elif 'rain' in weather:
                # Dibuja nubes grises y líneas inclinadas para simular lluvia
                draw.fill_color = Color('gray')
                draw.ellipse((200, 100), (80, 50))
                draw.ellipse((300, 80), (90, 60))
                draw.ellipse((400, 100), (80, 50))
                # Dibuja gotas de lluvia
                draw.stroke_color = Color('#ADD8E6')
                draw.stroke_width = 3
                for x in range(210, 400, 20):
                    draw.line((x, 140), (x - 10, 160))
            elif 'snow' in weather:
                # Dibuja nubes en tonos claros y pequeños copos de nieve
                draw.fill_color = Color('lightgray')
                draw.ellipse((250, 100), (80, 50))
                draw.ellipse((350, 80), (90, 60))
                draw.ellipse((450, 100), (80, 50))
                # Dibuja copos de nieve como pequeñas cruces
                draw.stroke_color = Color('white')
                draw.stroke_width = 2
                for x in range(260, 460, 30):
                    for y in range(140, 180, 20):
                        draw.line((x - 5, y - 5), (x + 5, y + 5))
                        draw.line((x - 5, y + 5), (x + 5, y - 5))
            elif 'thunderstorm' in weather:
                # Dibuja nubes oscuras y un rayo para tormenta
                draw.fill_color = Color('darkgray')
                draw.ellipse((200, 100), (80, 50))
                draw.ellipse((300, 80), (90, 60))
                draw.ellipse((400, 100), (80, 50))
                # Dibuja un rayo como polígono
                draw.fill_color = Color('#FFFF00')
                lightning_points = "300,120 320,150 290,150 310,180"
                draw.polygon(points=lightning_points)
            else:
                # Caso por defecto: una forma abstracta
                draw.fill_color = Color('red')
                draw.rectangle(left=250, top=150, width=270, height=300)

            # Dibuja la información textual en la imagen
            draw.font_size = 24
            draw.fill_color = Color('black')
            draw.text(20, 30, f"City: {city}")
            draw.text(20, 60, f"Temp: {temp}°C")
            draw.text(20, 90, f"Weather: {description}")

            draw(img)

        img.format = 'png'
        img_buffer = BytesIO()
        img.save(file=img_buffer)
        img_buffer.seek(0)
        return img_buffer

@app.route('/weather_image/<city>')
def weather_image(city):
    weather_data = get_weather(api_key, city)
    img_buffer = draw_weather(weather_data)
    return send_file(img_buffer, mimetype='image/png')

@app.route('/', methods=['GET', 'POST'])
def index():
    weather_data = None
    city = None
    if request.method == 'POST':
        city = request.form['city']
        weather_data = get_weather(api_key, city)
    return render_template('index.html', weather_data=weather_data, city=city, time=time)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
