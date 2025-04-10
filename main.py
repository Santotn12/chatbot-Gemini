#Este va a ser el main del proyecto el cual va a tener la logica del chatbot el cual utilizara la API de OpenAI para conectarse a Deep Seek   

import os
from dotenv import load_dotenv
import google.generativeai as genai
from logica_sheets import insertar_reclamo, autentificacion
import re

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configurar la API de Google Gemini
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise ValueError("No se encontró la variable de entorno GOOGLE_API_KEY. Por favor, configura tu archivo .env")

genai.configure(api_key=GOOGLE_API_KEY)

# Inicializar el modelo
model = genai.GenerativeModel('gemini-2.0-flash')

# Estado para el proceso de reclamo
estado_reclamo = {
    "en_proceso": False,
    "datos": {
        "id_cliente": None,
        "nombre": None,
        "correo": None,
        "descripcion": None
    },
    "intentos": {
        "id_cliente": 0,
        "nombre": 0,
        "correo": 0,
        "descripcion": 0
    }
}

# Información de contexto para la IA
INFORMACION_CONTEXTO = """
Eres un asistente virtual de atención al cliente. Tu función es responder preguntas sobre nuestros servicios y productos.
Información importante:
- Número de contacto: +54 2355573103
- Horario de atención: Lunes a Viernes de 9:00 AM a 6:00 PM
- Email de soporte: arielbergelin98@gmail.com
- Dirección: San Luis Tomas Jofre 930, San Luis

Solo debes responder preguntas relacionadas con la información proporcionada o con el proceso de reclamo.
Si el usuario tiene una pregunta que no está relacionada con la información proporcionada, indícale cortésmente que solo puedes responder preguntas sobre la información disponible o ayudarle con un reclamo.
"""

# Palabras clave para detectar intención de reclamo
PALABRAS_CLAVE_RECLAMO = [
    "problema", "error", "falla", "no funciona", "no sirve", "mal", "defecto", 
    "queja", "reclamo", "reportar", "reporte", "incidente", "solicitud", 
    "ayuda", "asistencia", "soporte", "arreglar", "reparar", "solucionar",
    "molesto", "insatisfecho", "disconforme", "decepcionado", "frustrado"
]

def detectar_intencion_reclamo(mensaje):
    """
    Detecta si el usuario tiene la intención de hacer un reclamo basado en palabras clave
    """
    mensaje_lower = mensaje.lower()
    
    # Verificar si contiene palabras clave de reclamo
    for palabra in PALABRAS_CLAVE_RECLAMO:
        if palabra in mensaje_lower:
            return True
            
    # Verificar patrones comunes de reclamo
    patrones_reclamo = [
        r"tengo un (problema|error|falla)",
        r"(no|no me) funciona",
        r"necesito (ayuda|asistencia|soporte)",
        r"quiero (reportar|reporte|reclamo)",
        r"hay (algo|un) (mal|error|problema)",
        r"estoy (molesto|insatisfecho|decepcionado)"
    ]
    
    for patron in patrones_reclamo:
        if re.search(patron, mensaje_lower):
            return True
            
    return False

def validar_campo(campo, valor):
    """
    Valida si el valor ingresado por el usuario corresponde al campo solicitado
    usando la API de Gemini
    """
    # Definir los criterios de validación para cada campo
    criterios = {
        "id_cliente": "El ID de cliente debe ser un identificador único, generalmente un número o código alfanumérico.",
        "nombre": "El nombre debe ser un nombre completo de persona, con nombre y apellido.",
        "correo": "El correo electrónico debe tener un formato válido (ejemplo@dominio.com).",
        "descripcion": "La descripción debe ser un texto que explique el problema o incidente que se está reportando."
    }
    
    # Crear el prompt para la validación
    prompt = f"""
    Eres un validador de datos. Tu tarea es determinar si el siguiente valor ingresado por un usuario 
    corresponde al campo '{campo}' que se le solicitó.
    
    Criterio de validación: {criterios[campo]}
    
    Valor ingresado por el usuario: "{valor}"
    
    Responde EXACTAMENTE con 'True' si el valor ingresado corresponde al campo solicitado, o 'False' si no corresponde.
    No agregues ninguna explicación adicional, solo 'True' o 'False'.
    """
    
    # Obtener la respuesta de Gemini
    response = model.generate_content(prompt)
    resultado = response.text.strip().lower()
    
    # Verificar si la respuesta es 'true' o 'false'
    return resultado == 'true'

def procesar_mensaje(mensaje):
    """
    Procesa el mensaje del usuario y genera una respuesta apropiada
    """
    # Verificar si el usuario quiere hacer un reclamo
    if "reportar incidente" in mensaje.lower() or "hacer reclamo" in mensaje.lower() or detectar_intencion_reclamo(mensaje):
        estado_reclamo["en_proceso"] = True
        return "Entiendo que deseas reportar un incidente o tienes un problema. Por favor, proporciona tu ID de cliente para comenzar el proceso."

    if estado_reclamo["en_proceso"]:
        return procesar_reclamo(mensaje)

    # Preparar el prompt con contexto para la IA
    prompt = f"{INFORMACION_CONTEXTO}\n\nPregunta del usuario: {mensaje}\n\nResponde solo con información relevante del contexto proporcionado. Si la pregunta no está relacionada con la información disponible, indícale cortésmente que solo puedes responder preguntas sobre la información disponible o ayudarle con un reclamo."
    
    # Generar respuesta usando Gemini
    response = model.generate_content(prompt)
    return response.text

def procesar_reclamo(mensaje):
    """
    Procesa los datos del reclamo paso a paso
    """
    # Validar el campo actual
    campo_actual = None
    if estado_reclamo["datos"]["id_cliente"] is None:
        campo_actual = "id_cliente"
    elif estado_reclamo["datos"]["nombre"] is None:
        campo_actual = "nombre"
    elif estado_reclamo["datos"]["correo"] is None:
        campo_actual = "correo"
    elif estado_reclamo["datos"]["descripcion"] is None:
        campo_actual = "descripcion"
    
    # Validar el valor ingresado
    if not validar_campo(campo_actual, mensaje):
        # Incrementar el contador de intentos
        estado_reclamo["intentos"][campo_actual] += 1
        
        # Verificar si se han excedido los intentos permitidos
        if estado_reclamo["intentos"][campo_actual] >= 3:
            # Reiniciar el estado del reclamo
            estado_reclamo["en_proceso"] = False
            estado_reclamo["datos"] = {
                "id_cliente": None,
                "nombre": None,
                "correo": None,
                "descripcion": None
            }
            estado_reclamo["intentos"] = {
                "id_cliente": 0,
                "nombre": 0,
                "correo": 0,
                "descripcion": 0
            }
            return "Lo siento, has excedido el número máximo de intentos para este campo. El proceso de reclamo ha sido cancelado por razones de seguridad. Por favor, intenta nuevamente más tarde o contacta a nuestro equipo de soporte directamente."
        
        # Mensaje de advertencia después del segundo intento
        if estado_reclamo["intentos"][campo_actual] == 2:
            return f"El valor ingresado no parece ser un {campo_actual} válido. Esta es tu última oportunidad para ingresar un valor correcto. Por favor, intenta nuevamente."
        
        # Mensaje de error después del primer intento
        return f"El valor ingresado no parece ser un {campo_actual} válido. Por favor, intenta nuevamente."
    
    # Si el valor es válido, continuar con el proceso
    if campo_actual == "id_cliente":
        estado_reclamo["datos"]["id_cliente"] = mensaje
        return "Gracias. Por favor, proporciona tu nombre completo."
    
    elif campo_actual == "nombre":
        estado_reclamo["datos"]["nombre"] = mensaje
        return "Gracias. Por favor, proporciona tu correo electrónico."
    
    elif campo_actual == "correo":
        estado_reclamo["datos"]["correo"] = mensaje
        return "Gracias. Por favor, describe el incidente o problema que deseas reportar."
    
    elif campo_actual == "descripcion":
        estado_reclamo["datos"]["descripcion"] = mensaje
        try:
            # Insertar el reclamo en Google Sheets
            client = autentificacion()
            insertar_reclamo(
                client,
                estado_reclamo["datos"]["id_cliente"],
                estado_reclamo["datos"]["nombre"],
                estado_reclamo["datos"]["correo"],
                estado_reclamo["datos"]["descripcion"]
            )
            # Reiniciar el estado
            estado_reclamo["en_proceso"] = False
            estado_reclamo["datos"] = {
                "id_cliente": None,
                "nombre": None,
                "correo": None,
                "descripcion": None
            }
            estado_reclamo["intentos"] = {
                "id_cliente": 0,
                "nombre": 0,
                "correo": 0,
                "descripcion": 0
            }
            return "¡Gracias! Tu reclamo ha sido registrado exitosamente. ¿Hay algo más en lo que pueda ayudarte?"
        except Exception as e:
            return f"Lo siento, hubo un error al registrar tu reclamo: {str(e)}"



