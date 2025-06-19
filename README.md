
# 🧠 Meme Generator AI — FastAPI + Gemini + PIL

Una API simple y divertida que analiza imágenes utilizando Gemini AI de Google, genera frases graciosas y superpone el texto en la imagen al estilo de un meme clásico. Ideal para entretenimiento, creación de contenido o demostraciones de IA multimodal.

---

## 🚀 Características

- 📷 Subida de imágenes (PNG, JPG)
- 💬 Generación automática de frases ingeniosas (máx. 10 palabras)
- 🧠 Análisis visual usando Gemini (modelo multimodal)
- ✍️ Superposición automática de texto con visibilidad garantizada
- 🖥️ Interfaz web minimalista con FastAPI + Jinja2
- 🌐 API disponible para integraciones externas

---

## ⚙️ Requisitos

- Python 3.9 o superior
- Cuenta en Google AI Studio con API Key activa
- Modelos compatibles: `gemini-1.5-flash`, `gemini-2.0-flash` (requiere entrada de imagen)

---

## 📦 Instalación

```bash
# Clona este repositorio
git clone https://github.com/tuusuario/meme-generator-ai.git
cd meme-generator-ai

# Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows usa venv\Scripts\activate

# Instala las dependencias
pip install -r requirements.txt
```

---

## 🧪 Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto y añade:

```env
GEMINI_API_KEY=tu_clave_api_de_google
IA_GENERATIVE_MODEL=gemini-1.5-flash  # o gemini-2.0-flash si soporta imágenes
```

---

## ▶️ Ejecución

```bash
uvicorn main:app --reload
```

Abre tu navegador en [http://localhost:8000](http://localhost:8000)

---

## 📁 Estructura del Proyecto

```
meme-generator-ai/
├── main.py                  # API principal con FastAPI
├── templates/
│   └── index.html           # Interfaz web para subir imágenes
├── ARIAL.TTF                # Fuente utilizada para el texto del meme
├── .env                     # Claves y configuración
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Documentación
```

---

## 🧠 ¿Cómo funciona?

1. Subes una imagen desde la web.
2. El backend genera un prompt con instrucciones claras y lo envía junto con la imagen a Gemini.
3. Gemini devuelve una frase graciosa y breve.
4. La frase se superpone sobre la imagen utilizando Pillow (PIL).
5. La imagen resultante se devuelve al usuario como una respuesta directa.

---

## 🖼️ Ejemplo de uso

1. Sube una imagen divertida (por ejemplo, una expresión facial cómica).
2. El sistema generará una frase como:
   > "Cuando dices 'sí' sin entender la reunión."
3. Y obtendrás la imagen con esa frase centrada y visible al estilo meme.

---

## 📌 Notas importantes

- Si el modelo Gemini no acepta imágenes, usa `gemini-1.5-flash`.
- Asegúrate de tener una fuente `.ttf` en el mismo directorio (por ejemplo, `ARIAL.TTF`).
- Puedes cambiar la fuente editando `FONT_PATH` en `main.py`.

---

## 📜 Licencia

MIT © 2025 — Desarrollado por José Manuel Sanz

---

## 💡 Futuras mejoras

- Soporte para textos arriba y abajo (formato meme clásico)
- Modo oscuro en la interfaz web
- Traducción automática del texto generado
- Integración con Telegram o WhatsApp