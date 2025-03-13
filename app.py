from flask import Flask, render_template, request, send_file
import requests
from dotenv import load_dotenv
import os
from wand.image import Image
from wand.drawing import Drawing
from wand.color import Color
from io import BytesIO

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
    weather = weather_data['weather'][0]['main'].lower()  # Condición climática (nubes, lluvia, etc.)
    description = weather_data['weather'][0]['description']

    # Crear una imagen en memoria
    with Image(width=600, height=400, background=Color('#87CEEB')) as img:
        with Drawing() as draw:
            # Dibujar el fondo (cielo)
            draw.fill_color = Color('#87CEEB')  # Azul cielo
            draw.rectangle(left=0, top=0, width=600, height=400)

            # Dibujar el suelo
            draw.fill_color = Color('#32CD32')  # Verde pasto
            draw.rectangle(left=0, top=300, width=600, height=400)

            # Dibujar una representación visual del clima
            if 'cloud' in weather:
                # Dibujar nubes
                draw.fill_color = Color('white')
                draw.circle((150, 150), (100, 120))  # Nube 1
                draw.circle((250, 150), (200, 140))  # Nube 2
                draw.circle((350, 150), (300, 130))  # Nube 3
            elif 'rain' in weather:
                # Dibujar lluvia
                draw.fill_color = Color('#ADD8E6')  # Azul claro
                for i in range(10):
                    draw.rectangle(left=100 + i * 50, top=200, width=110 + i * 50, height=220)  # Gotas de lluvia
            elif 'clear' in weather:
                # Dibujar un sol
                draw.fill_color = Color('#FFD700')  # Amarillo dorado
                draw.circle((300, 100), (250, 50))  # Sol
            elif 'snow' in weather:
                # Dibujar nieve
                draw.fill_color = Color('white')
                for i in range(10):
                    draw.circle((100 + i * 50, 200), (90 + i * 50, 190))  # Copos de nieve
            elif 'thunderstorm' in weather:
                # Dibujar una tormenta eléctrica
                draw.fill_color = Color('#808080')  # Gris
                draw.rectangle(left=100, top=100, width=500, height=200)  # Nube de tormenta
                draw.fill_color = Color('#FFFF00')  # Amarillo
                draw.rectangle(left=200, top=150, width=210, height=250)  # Rayo
            else:
                # Dibujar un icono genérico (termómetro)
                draw.fill_color = Color('red')
                draw.rectangle(left=250, top=150, width=270, height=300)  # Termómetro

            # Dibujar el texto
            draw.font_size = 24
            draw.fill_color = Color('black')
            draw.text(50, 30, f"City: {city}")
            draw.text(50, 70, f"Temperature: {temp}°C")
            draw.text(50, 110, f"Weather: {description}")

            draw(img)

        # Convertir la imagen a un formato PNG
        img_buffer = BytesIO()
        img.save(file=img_buffer, format='png')
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
    return render_template('index.html', weather_data=weather_data, city=city)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

