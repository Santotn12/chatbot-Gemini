# Chatbot de Ariel Developer

Un chatbot inteligente que utiliza la API de Google Gemini para responder consultas de clientes y gestionar reclamos.

## Características

- Respuestas inteligentes a consultas de clientes
- Detección automática de intenciones de reclamo
- Proceso guiado para crear reclamos
- Validación de datos ingresados por el usuario
- Almacenamiento de reclamos en Google Sheets

## Requisitos

- Python 3.8 o superior
- Cuenta de Google Cloud con API de Gemini habilitada
- Cuenta de Google Sheets para almacenar los reclamos

## Instalación local

1. Clona este repositorio:
```bash
git clone https://github.com/tu-usuario/chatbot-ariel.git
cd chatbot-ariel
```

2. Instala las dependencias:
```bash
pip install -r requirements.txt
```

3. Crea un archivo `.env` en la raíz del proyecto con tu clave API de Google:
```
GOOGLE_API_KEY=tu_clave_api_aqui
```

4. Ejecuta la aplicación:
```bash
streamlit run front.py
```

## Despliegue en Streamlit Cloud

1. Crea una cuenta en [Streamlit Cloud](https://streamlit.io/cloud)
2. Conecta tu repositorio de GitHub
3. Configura la variable de entorno `GOOGLE_API_KEY` en la configuración de la aplicación
4. ¡Listo! 

## Estructura del proyecto

- `front.py`: Interfaz de usuario con Streamlit
- `main.py`: Lógica del chatbot y procesamiento de mensajes
- `logica_sheets.py`: Funciones para interactuar con Google Sheets
- `requirements.txt`: Dependencias del proyecto
- `.env`: Variables de entorno (no incluido en el repositorio)

## Uso

1. Inicia la aplicación
2. Haz preguntas sobre información de contacto, horarios, etc.
3. Para reportar un problema, describe tu situación y el chatbot te guiará en el proceso
4. Sigue las instrucciones para completar el formulario de reclamo

## Notas importantes

- La aplicación valida los datos ingresados durante el proceso de reclamo
- Tienes hasta 3 intentos para ingresar datos correctos
- Después del tercer intento fallido, el proceso se cancela por seguridad 
