from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv()  # Cargar variables de entorno desde el archivo .env

# Verificación de la API Key
api_key = os.getenv("API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    print("¡Error! No se pudo cargar la clave de API desde el archivo .env.")

app = Flask(__name__)
CORS(app)

@app.route("/generar-quiz", methods=["POST"])
def generar_quiz():
    try:
        # Obtener los datos enviados en la solicitud
        data = request.get_json()
        tema = data.get("tema")
        tipo = data.get("tipo")

        # Validar que los datos sean correctos
        if not tema or not tipo:
            return jsonify({"error": "Se requiere un tema y un tipo de pregunta."}), 400

        # Prompt mejorado
        prompt = (
            f"Genera 5 preguntas de tipo {tipo} sobre {tema}."
            " Formato: "
            "\nPregunta: (Aquí la pregunta)"
            "\nA) (Opción 1)"
            "\nB) (Opción 2)"
            "\nC) (Opción 3)"
            "\nD) (Opción 4)"
            "\nRespuesta correcta: (Letra de la opción correcta)"
            "\n\nRepite este formato para 5 preguntas."
        )

        # Configuración del modelo
        modelo = genai.GenerativeModel("gemini-1.5-pro-latest")
        respuesta = modelo.generate_content(prompt)

        # Procesar respuesta
        quiz_data = procesar_respuesta(respuesta.text)

        return jsonify(quiz_data)

    except Exception as e:
        print(f"Error en generar_quiz: {str(e)}")
        return jsonify({"error": f"Ocurrió un error: {str(e)}"}), 500

def procesar_respuesta(respuesta):
    try:
        preguntas = []
        bloques = respuesta.strip().split("\n\n")  # Separar por bloques

        for bloque in bloques:
            lineas = bloque.strip().split("\n")
            if len(lineas) < 6:  # Asegurar que hay suficientes líneas
                continue

            pregunta = lineas[0].replace("Pregunta:", "").strip()
            opciones = [lineas[i].strip() for i in range(1, 5)]
            respuesta_correcta = lineas[5].replace("Respuesta correcta:", "").strip()

            preguntas.append({
                "pregunta": pregunta,
                "opciones": opciones,
                "respuesta_correcta": respuesta_correcta
            })

        return {"preguntas": preguntas}

    except Exception as e:
        return {"error": "No se pudo procesar la respuesta: " + str(e)}

if __name__ == "__main__":
    app.run(debug=True)
