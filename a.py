from flask import Flask, request, jsonify 
from flask_cors import CORS
import os
import google.generativeai as genai
model = genai.GenerativeModel("gemini-1.5-flash")
from dotenv import load_dotenv
from supabase import create_client, Client
import boto3
import io 
from datetime import datetime
import fitz
import base64
from io import BytesIO

load_dotenv()
api_key = os.getenv('API_KEY')
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
AWS_AK = os.getenv('AWS_AK')
AWS_SAK = os.getenv('AWS_SAK')

supabase: Client = create_client(url, key)
genai.configure(api_key=api_key) 
polly = boto3.client('polly', region_name='us-east-1',aws_access_key_id=AWS_AK,aws_secret_access_key=AWS_SAK)  # Cambia a tu región preferida

app = Flask(__name__)
CORS(app)  # Permite solicitudes desde cualquier origen

num = 0

@app.route('/auth/signOut', methods=['POST'])
def auth_sign_out():
    response = supabase.auth.sign_out()

@app.route('/auth/login', methods=['POST'])
def auth_login():
    data = request.get_json()
    print(data)
    email = data.get('email','')
    password = data.get('password','')

    if not email or not password:
        return jsonify({'Error': "Faltan credenciales"}), 400

    try:
        response = supabase.auth.sign_in_with_password(
            {"email": email, "password": password}
        )
        if not response:
            raise ValueError(response)
        
        access_token = response.session.access_token

        # Devolver el mensaje junto con el JWT
        return jsonify({'Mensaje': 'Inicio de sesión exitoso', 'JWT': access_token}), 200

        
    except Exception as e:
        return jsonify({'Error': str(e)}), 500


@app.route('/auth/singUp', methods=['POST'])
def auth_sing_up():
    data = request.get_json()
    email = data.get('email','')
    password = data.get('password','')

    if not email or not password:
        return jsonify({'Error': "Faltan credenciales"}), 400

    try:
        response = supabase.auth.sign_up({
            'email': email,
            'password': password,
        })

        if not response:
            raise ValueError(response)

        return jsonify({'Mensaje': 'Registro exitoso'}), 201

    except Exception as e:
        return jsonify({'Error': str(e)}), 500

@app.route('/texto', methods=['POST'])
def handel():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'Error': "No se proporcionó un token válido"}), 401

    token = auth_header.split(" ")[1]  # Extraer el token después de 'Bearer'
    
    # Verificar si el usuario está autenticado
    usuario = verificar_token(token)
    if not usuario:
        return jsonify({'Error': "Usuario no autenticado"}), 401

    data = request.get_json()
    texto = data.get('text', '')
    
    if not texto:
        return jsonify({'Respuesta': "No se puedo obtener el texto de la peticion" }), 404
    
    try:
        respuesta_geminai = handel_text(texto)
        if not respuesta_geminai:
            raise ValueError("Error generando el texto con GeminiAI")
        
        respuesta_polly = handel_audio(respuesta_geminai.replace("#", ""))
        if not respuesta_polly:
            raise ValueError("Error generando el audio con Amazon Polly")

        respuesta_bucket_supabase = handel_bucket_supabase(respuesta_polly, usuario)
        if not respuesta_bucket_supabase:
            raise ValueError("Error subiendo el audio al bucket de Supabase")
        now = datetime.now().isoformat()  # Usar formato ISO 8601
        response = (
            supabase.table("messenge")
            .insert({
                "message_text": respuesta_geminai,
                "audio_link": respuesta_bucket_supabase,
                "message_time": now,  # Aquí pasa el timestamp en el formato adecuado
                "user_id": usuario.user.id,
            })
            .execute()
        )

        if not response:
            raise ValueError("Error no se pudo registrar el dato")

        return jsonify({
            'Respuesta_Geminai': respuesta_geminai,
            'Audio_URL': respuesta_bucket_supabase
        }), 200

    except Exception as e:
        return jsonify({'Error': str(e)}), 500
    
@app.route('/historial', methods=['GET'])
def get_historial():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'Error': "No se proporcionó un token válido"}), 401

    token = auth_header.split(" ")[1]
    usuario = verificar_token(token)
    if not usuario:
        return jsonify({'Error': "Usuario no autenticado"}), 401
    
    try:
        response = (
            supabase.table("messenge")
            .select("id", "message_text", "audio_link", "image_link", "message_time")
            .eq("user_id", usuario.user.id)
            .execute()
        )
        
        if not response.data:
            return jsonify({'Error': "No hay datos disponibles en la consulta"}), 404


        return jsonify({
            'Respuesta': response.data,
        }), 200

    except Exception as e:
        return jsonify({'Error': str(e)}), 500

def handel_text(texto):
    response = model.generate_content(f"del siguiente texto califica la escritura, la gramatica y el sentido del mismo texto {texto}")
    return response.text
    
def handel_audio(texto):
    response = polly.synthesize_speech(
        Text=texto,
        OutputFormat='mp3',
        VoiceId='Conchita'
    )
    if 'AudioStream' in response:
        # Usar un buffer en memoria para almacenar el audio temporalmente
        audio_stream = io.BytesIO(response['AudioStream'].read())
        return audio_stream
    return None 
        
def handel_bucket_supabase(AudioStream,user):
    audio_content = AudioStream.getvalue()
    now = datetime.now()
    time_create = now.strftime("%Y%m%d-%H%M%S")

    upload_response = supabase.storage.from_("audios").upload(
        f"{user.user.id}-{time_create}.mp3", audio_content, file_options={"content-type": "audio/mpeg"}
    )
    if upload_response:
        public_url = supabase.storage.from_("audios").get_public_url(f"{user.user.id}-{time_create}.mp3")
        return public_url  # Retorna el enlace público
    return None

def verificar_token(token):
    try:
        user = response = supabase.auth.get_user(token)
        if user:
            return user
        return None
    except Exception as e:
        print(f"Error verificando token: {str(e)}")
        return None

@app.route('/file', methods=['POST'])
def process_base64_pdf():
    # Obtén el contenido en base64 y el nombre del archivo del JSON
    data = request.json.get('file')
    filename = request.json.get('filename')
    
    if not data:
        return jsonify({"error": "No se encontró el archivo en base64"}), 400
    if not filename:
        return jsonify({"error": "No se encontró el nombre del archivo"}), 400

    # Decodifica el PDF base64
    try:
        pdf_data = base64.b64decode(data)
        pdf_stream = BytesIO(pdf_data)

        # Abre el PDF desde el flujo de bytes
        pdf_document = fitz.open(stream=pdf_stream, filetype="pdf")
        
        # Imprime información del archivo en la consola
        print(f"Nombre del archivo: {filename}")
        print("Número de páginas:", pdf_document.page_count)
        for i in range(pdf_document.page_count):
            page = pdf_document[i]
            print(f"Contenido de la página {i + 1}:\n", page.get_text())

        pdf_document.close()
        
        return jsonify({"message": "PDF procesado correctamente"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)