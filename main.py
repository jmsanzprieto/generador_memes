# main.py
import os
from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv
import google.generativeai as genai
from PIL import Image, ImageDraw, ImageFont
import io

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener la API Key de Gemini desde las variables de entorno
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Obtener el nombre del modelo de Gemini desde las variables de entorno,
# con un valor predeterminado si no se especifica.
IA_GENERATIVE_MODEL = os.getenv("IA_GENERATIVE_MODEL", "gemini-2.0-flash")


if not GEMINI_API_KEY:
    raise RuntimeError("La variable de entorno GEMINI_API_KEY no está configurada. Por favor, asegúrate de tener un archivo .env con tu clave.")

# Configurar la API de Gemini
genai.configure(api_key=GEMINI_API_KEY)

# Inicializar el modelo Gemini con el nombre obtenido de las variables de entorno
try:
    model = genai.GenerativeModel(IA_GENERATIVE_MODEL)
    # Es crucial que el modelo seleccionado (IA_GENERATIVE_MODEL) soporte entrada multimodal (texto e imagen).
    # 'gemini-1.5-flash' es una buena opción para esto si 'gemini-2.0-flash' da problemas con imágenes.
except Exception as e:
    raise RuntimeError(f"Error al inicializar el modelo de Gemini '{IA_GENERATIVE_MODEL}': {e}. Asegúrate de que el modelo sea válido y soporte el análisis de imágenes.")


app = FastAPI(
    title="Análisis de Imágenes con Gemini AI",
    description="Una API simple para subir imágenes, obtener descripciones humorísticas y superponerlas en la imagen.",
    version="1.0.0"
)

# Configurar la ruta para las plantillas HTML
templates = Jinja2Templates(directory="templates")

# Define la ruta de la fuente. Asegúrate de tener un archivo de fuente (.ttf) en el mismo directorio.
# Puedes cambiar esto por "Roboto-Regular.ttf" o cualquier otra que uses.
# Si no tienes una, intenta usar "arial.ttf" o descarga una.
FONT_PATH = "ARIAL.TTF"

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Muestra la página principal con el formulario para subir imágenes.
    """
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze_image/")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analiza una imagen subida, genera una frase divertida y la superpone en la imagen.

    Args:
        file (UploadFile): La imagen a analizar (JPEG, PNG, etc.).

    Returns:
        StreamingResponse: La imagen modificada con la frase superpuesta.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Tipo de archivo no soportado. Por favor, sube una imagen."
        )

    try:
        # Leer el contenido de la imagen
        image_data = await file.read()
        original_image_format = file.content_type # Guardar el formato original

        # Abrir la imagen usando Pillow (PIL)
        img = Image.open(io.BytesIO(image_data)).convert("RGB") # Convertir a RGB para asegurar compatibilidad con diferentes formatos de imagen.

        # Crear el prompt para Gemini, pidiendo una sola frase divertida de no más de 10 palabras
        prompt_message = (
            """ Propósito y Objetivos:
                * Analizar imágenes proporcionadas para capturar su esencia visual y emocional.
                * Generar una única frase ingeniosa, de no más de 10 palabras, que complemente la imagen y sea adecuada para un meme viral.
                * Asegurarse de que el humor sea simpático, original, y libre de vulgaridades u ofensas.
                * Utilizar la ironía, el sarcasmo ligero o los juegos de palabras cuando sea apropiado para realzar el ingenio.

                Comportamientos y Reglas:
                1) Análisis de Imagen y Reacción Inicial:
                    a) Espera la imagen proporcionada por el usuario.
                    b) Evalúa el tono visual, las expresiones, el contexto y cualquier elemento que pueda ser fuente de humor.
                c) Si la imagen es ambigua, puedes pedir una aclaración sutilmente, pero prioriza la generación de una frase.

                2) Generación de la Frase:
                    a) La frase debe ser concisa (máximo 10 palabras), impactante y memorable.
                    b) Debe ser original y no reutilizar memes existentes a menos que se le indique explícitamente al usuario que está buscando un 'remix' de memes.
                    c) Evita el lenguaje soez, los chistes ofensivos, o cualquier contenido que pueda ser considerado políticamente incorrecto o insensible.
                    d) Enfócate en el humor visual o situacional que la imagen sugiere.
                    e) La frase debe ser adecuada para el formato de un meme clásico (texto sobre imagen).

                3) Interacción:
                    a) Presenta la frase de forma directa y clara, y en español.

                Tono General:
                    * Creativo y con un toque de ingenio.
                    * Simpático y accesible.
                    * Respetuoso y no ofensivo.
                    * Directo y conciso en sus respuestas. """
        )

        # Enviar la imagen y el prompt al modelo Gemini
        response = model.generate_content([prompt_message, img])
        funny_sentence = response.text.strip() # Eliminar espacios en blanco extras

        # --- Medida de seguridad: Asegurar una sola línea y máximo 10 palabras ---
        funny_sentence = funny_sentence.split('\n')[0] # Tomar solo la primera línea
        words = funny_sentence.split()
        if len(words) > 10:
            # Si tiene más de 10 palabras, truncar y añadir puntos suspensivos
            funny_sentence = ' '.join(words[:10]) + '...'


        # --- Superponer la frase en la imagen ---
        draw = ImageDraw.Draw(img)
        img_width, img_height = img.size

        # Intentar cargar la fuente y ajustar su tamaño dinámicamente
        font = None
        try:
            # Empezar con un tamaño de fuente generoso (ej. 5% de la altura de la imagen)
            font_size = int(img_height * 0.05)
            font = ImageFont.truetype(FONT_PATH, font_size)

            # Ajustar el tamaño de la fuente para que el texto quepa dentro del 90% del ancho de la imagen
            # Esto evita que el texto se desborde horizontalmente.
            max_text_width = img_width * 0.9
            while True:
                # textbbox devuelve (left, top, right, bottom)
                left, top, right, bottom = draw.textbbox((0,0), funny_sentence, font=font)
                text_width = right - left
                text_height = bottom - top # Esto es la altura de una sola línea de texto

                if text_width < max_text_width:
                    break # La fuente es lo suficientemente pequeña, salimos del bucle
                
                font_size -= 1 # Reducir el tamaño de la fuente
                if font_size <= 10: # Evitar que la fuente sea demasiado pequeña para leer
                    font = ImageFont.truetype(FONT_PATH, 10)
                    break
                font = ImageFont.truetype(FONT_PATH, font_size)

        except IOError:
            print(f"Advertencia: La fuente '{FONT_PATH}' no se encontró. Usando la fuente predeterminada.")
            font = ImageFont.load_default()
            # Cuando se usa font.load_default(), el tamaño es fijo y no se puede ajustar fácilmente.
            # Para un control de tamaño efectivo y que destaque, es crucial usar una fuente .ttf.
            left, top, right, bottom = draw.textbbox((0,0), funny_sentence, font=font)
            text_width = right - left
            text_height = bottom - top


        # Calcular la posición del texto
        # Centrado horizontalmente
        x = (img_width - text_width) / 2
        # Posición vertical en el cuarto inferior, con un pequeño margen desde el borde inferior
        # Aproximadamente el 90% de la altura de la imagen.
        y = img_height - text_height - int(img_height * 0.05) # 5% de margen desde abajo

        # Dibujar el texto con un contorno para mayor visibilidad
        # Color del texto (blanco)
        text_color = (255, 255, 255)
        # Color del contorno (negro)
        outline_color = (0, 0, 0)
        outline_width = 3 # Ancho del contorno

        # Dibujar el contorno
        for dx in [-outline_width, 0, outline_width]:
            for dy in [-outline_width, 0, outline_width]:
                draw.text((x + dx, y + dy), funny_sentence, font=font, fill=outline_color)

        # Dibujar el texto principal
        draw.text((x, y), funny_sentence, font=font, fill=text_color)


        # Guardar la imagen modificada en un buffer de bytes
        img_byte_arr = io.BytesIO()
        # Usa el formato de imagen original si es posible, de lo contrario JPEG
        if original_image_format in ["image/png", "image/jpeg"]:
            img.save(img_byte_arr, format=original_image_format.split('/')[1].upper())
        else:
            # Default to JPEG if format is unknown or not directly supported for saving
            img.save(img_byte_arr, format="JPEG")

        img_byte_arr.seek(0) # Mover el cursor al principio del buffer

        # Devolver la imagen modificada como respuesta
        return StreamingResponse(img_byte_arr, media_type=original_image_format)

    except Exception as e:
        # Manejo de errores general
        print(f"Error al procesar la imagen: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Ocurrió un error al procesar tu imagen: {str(e)}. Asegúrate de que el modelo Gemini seleccionado soporta entrada de imágenes y que la fuente '{FONT_PATH}' está en el directorio correcto."
        )

# Este bloque es para ejecutar la aplicación directamente con Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
