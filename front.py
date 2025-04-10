from ast import main
import streamlit as st
from main import procesar_mensaje

#Este archivo va a tener la logica para la interfaz de usuario de la aplicacion
#---Titulo----
st.title("🚀Chatbot de Ariel developer🚀")

# Agregar información de contacto en la barra lateral
with st.sidebar:
    st.header("📞 Información de Contacto")
    st.write("**Teléfono:** +54 2355573103")
    st.write("**Email:** arielbergelin98@gmail.com")
    st.write("**Horario:** Lunes a Viernes de 9:00 AM a 6:00 PM")
    st.write("**Dirección:** San Luis Tomas Jofre 930, San Luis")
    
    st.header("💡 Consejos")
    st.write("Puedes preguntar sobre:")
    st.write("- Información de contacto")
    st.write("- Horarios de atención")
    st.write("- Proceso de reclamos")
    st.write("- Cualquier duda sobre nuestros servicios")
    
    st.write("Para reportar un problema, simplemente describe tu situación y te ayudaré a crear un reclamo.")
    
    st.header("⚠️ Validación de Datos")
    st.write("Durante el proceso de reclamo, se validará la información que ingreses.")
    st.write("Si ingresas datos incorrectos, tendrás hasta 3 intentos para corregirlos.")
    st.write("Después del tercer intento fallido, el proceso se cancelará por seguridad.")

#Estado para almacenar el historial de la conversacion
if 'messages' not in st.session_state:
    st.session_state.messages = []

#Flag para verificar si el usuario ingresa por primera vez a la aplicacion
if "first_message" not in st.session_state: 
    st.session_state.first_message = True

#---Mensaje de bienvenida----
if st.session_state.first_message:
    
    st.session_state.messages.append({"role": "assistant", "content": "👋 **¡Bienvenido al chatbot de Ariel developer!**\n\nSoy tu asistente virtual y estoy aquí para ayudarte con cualquier consulta sobre nuestros servicios o para guiarte en el proceso de reclamo.\n\nPuedes preguntarme sobre información de contacto, horarios, o simplemente describir cualquier problema que tengas y te ayudaré a crear un reclamo.\n\n**Importante:** Durante el proceso de reclamo, se validará la información que ingreses. Si ingresas datos incorrectos, tendrás hasta 3 intentos para corregirlos."})
    st.session_state.first_message = False

# Mostrar el historial de mensajes
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Escribe tu mensaje:"):
    # Mostrar el mensaje del usuario
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Procesar el mensaje y obtener la respuesta
    respuesta = procesar_mensaje(prompt)

    # Mostrar la respuesta del asistente
    with st.chat_message("assistant"):
        st.markdown(respuesta)
    st.session_state.messages.append({"role": "assistant", "content": respuesta})

#--------------------------------Chat--------------------------------






