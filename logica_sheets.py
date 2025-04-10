import os
import csv
import logging
import datetime
import gspread
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials

# Configuración del logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de autenticación
CREDENTIALS_FILE = "c:\\Users\\Usuario\\Desktop\\python\\chatbot\\credencial\\chatbot-deepsek-1716c72dcfcd.json"
SCOPE = ['https://spreadsheets.google.com/feeds',
         'https://www.googleapis.com/auth/drive']

# Nombre del documento global en Google Sheets y nombre del hoja_trabajo principal
SPREADSHEET_NAME = "Reclamos_Clientes"
hoja_trabajo_TITLE = "Reclamos"

columnas = ["Fecha","ID Cliente","Nombre","Descripcion","Nivel prioridad"]

carpeta_a_exportar = "export"

def autentificacion():
    """Autentica usando el archivo de credenciales o la variable de entorno y retorna el cliente de gspread."""
    try:
        # Intentar obtener credenciales desde la variable de entorno
        creds_json_base64 = os.getenv("GOOGLE_SHEETS_CREDENTIALS")
        
        if creds_json_base64:
            # Decodificar la cadena base64 a JSON
            creds_json = base64.b64decode(creds_json_base64).decode('utf-8')
            creds_dict = json.loads(creds_json)
            
            # Crear credenciales desde el diccionario
            creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, SCOPE)
            client = gspread.authorize(creds)
            logging.info("Autenticación exitosa con Google Sheets usando variable de entorno.")
            return client
        else:
            # Usar el archivo de credenciales local
            creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENTIALS_FILE, SCOPE)
            client = gspread.authorize(creds)
            logging.info("Autenticación exitosa con Google Sheets usando archivo local.")
            return client
    except Exception as e:
        logging.error(f"Error en la autenticación: {e}")
        raise

def obtener_hoja_trabajo(client, spreadsheet_title, worksheet_title, columnas):
    try:
        # Obtener o crear el spreadsheet
        try:
            spreadsheet = client.open(spreadsheet_title)
            logging.info(f"Spreadsheet '{spreadsheet_title}' encontrado.")
        except gspread.SpreadsheetNotFound:
            spreadsheet = client.create(spreadsheet_title)
            logging.info(f"Spreadsheet '{spreadsheet_title}' no encontrado, creado uno nuevo.")

        # Obtener o crear la hoja de trabajo
        try:
            worksheet = spreadsheet.worksheet(worksheet_title)
            logging.info(f"Worksheet '{worksheet_title}' encontrado.")
        except gspread.WorksheetNotFound:
            worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows="100", cols=str(len(columnas)))
            logging.info(f"Worksheet '{worksheet_title}' no encontrado, creado uno nuevo.")
            worksheet.append_row(columnas)

        return worksheet

    except Exception as e:
        logging.error(f"Error al obtener o crear la hoja de trabajo: {e}")
        raise

def insertar_nueva_fila(hoja_trabajo,datos):
    """
    Inserta una nueva fila en el hoja_trabajo.
    claim_data debe ser una lista con los siguientes elementos:
    [Fecha, ID Cliente, Nombre, Correo, Descripción]
    """
    try:
        hoja_trabajo.append_row(datos)
        logging.info("Reclamo insertado exitosamente en la hoja.")
    except Exception as e:
        logging.error(f"Error al insertar el reclamo: {e}")
        raise

def descargar_hoja_trabajo_a_csv(hoja_trabajo, carpeta_a_exportar):
    """
    Descarga el contenido del hoja_trabajo y lo guarda en un archivo CSV en la carpeta carpeta_a_exportar.
    El nombre del archivo incluirá el nombre del hoja_trabajo y la fecha/hora de exportación.
    """
    try:
        # Asegurarse de que la carpeta de exportación exista
        if not os.path.exists(carpeta_a_exportar):
            os.makedirs(carpeta_a_exportar)
            logging.info(f"Carpeta '{carpeta_a_exportar}' creada para exportaciones.")
        
        # Obtener todos los valores del hoja_trabajo
        data = hoja_trabajo.get_all_values()
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        file_name = f"{hoja_trabajo.title}_{timestamp}.csv"
        file_path = os.path.join(carpeta_a_exportar, file_name)
        
        # Guardar en formato CSV
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        
        logging.info(f"hoja_trabajo exportado correctamente a: {file_path}")
        return file_path
    except Exception as e:
        logging.error(f"Error al exportar el hoja_trabajo: {e}")
        raise

def insertar_reclamo(client, id_cliente, nombre, correo, descripcion):
    """
    Función central que:
      - Obtiene o crea el spreadsheet y worksheet.
      - Inserta el reclamo con los datos proporcionados.
      - Descarga la hoja actualizada en formato CSV.
    """
    try:
        worksheet = obtener_hoja_trabajo(client, SPREADSHEET_NAME, hoja_trabajo_TITLE, columnas)
        
        # Generar la fecha actual en formato deseado
        fecha = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # Preparar la fila con la información del reclamo
        claim_row = [fecha, id_cliente, nombre, correo, descripcion]
        
        # Insertar la fila en la hoja
        insertar_nueva_fila(worksheet, claim_row)
        
        # Exportar la hoja actualizada
        csv_file_path = descargar_hoja_trabajo_a_csv(worksheet, carpeta_a_exportar)
        
        return csv_file_path
    except Exception as e:
        logging.error(f"Error en el proceso de inserción del reclamo: {e}")
        raise

# Función para simular el flujo de reclamo en el chatbot
def proceso_iniciar_reclamo():
    """
    Simula el flujo en el que el chatbot recopila los datos y se almacena el reclamo.
    En un entorno real, estos datos vendrían del frontend o la API del chatbot.
    """
    try:
        client = autentificacion()
        
        # Simulación: datos recopilados del cliente
        id_cliente = "Arielin"
        nombre = "Arielin"
        correo = "Arielin@example.com"
        descripcion = "Soy muy malo jugando al lol."
        
        # Insertar el reclamo y obtener la ruta del archivo CSV exportado
        archivo_exportado = insertar_reclamo(client, id_cliente, nombre, correo, descripcion)
        logging.info(f"Proceso completado. Archivo exportado: {archivo_exportado}")
    except Exception as e:
        logging.error(f"Error en el proceso de reclamo: {e}")

if __name__ == "__main__":
    proceso_iniciar_reclamo()