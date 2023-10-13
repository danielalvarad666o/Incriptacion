from flask import Flask, request, render_template, send_file, flash as flask_flash
from cryptography.fernet import Fernet
import os
import mysql.connector
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

app = Flask(__name__)

BotonyInput =True
smtp_server = 'smtp.mailgun.org'
smtp_port = 587
smtp_username = 'postmaster@sandboxbce62b36a3b2454f997c50daa240a848.mailgun.org'
smtp_password = 'fef61d3b49108a88f9f31ca81e3d680b-77316142-79a8c6d2'

def enviar_correo(mensaje_encriptado, destinatario):
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)

        message = MIMEMultipart()
        message['From'] = smtp_username
        message['To'] = destinatario
        message['Subject'] = 'Mensaje encriptado'

        body = 'Este es el Archivo para desencriptar .'
        message.attach(MIMEText(body, 'plain'))

        # Adjunta el archivo .key
        key_attachment = MIMEApplication(mensaje_encriptado, Name='clave.key')
        message.attach(key_attachment)

        server.sendmail(smtp_username, destinatario, message.as_string())
        server.quit()

        print('Correo enviado con éxito.', 'success')
    except Exception as e:
        print(f'Error al enviar el correo: {str(e)}', 'danger')

# Funciones para manejar la encriptación

def genera_Clave():
    clave = Fernet.generate_key()
    with open("Clave.key", "wb") as archivo_clave:
        archivo_clave.write(clave)

def cargar_clave():
    if not os.path.exists("Clave.key"):
        genera_Clave()
    return open("Clave.key", "rb").read()

# Configura la clave secreta de Flask utilizando la clave generada
app.secret_key = cargar_clave()

@app.route('/')
def index():
    return render_template('index.html', encrypted_message=" ",BotonyInput=True)

@app.route('/encrypt_server', methods=['POST'])
def encrypt_server():
    clave_original = app.secret_key  # Guarda la clave secreta original
    genera_Clave()  # Genera una nueva clave temporal para la encriptación
    clave_temporal = cargar_clave()
    
    mensaje = request.form['message'].encode()
    f = Fernet(clave_temporal)
    
    try:
        encriptando = f.encrypt(mensaje)
        print(encriptando)
        cursor.execute("INSERT INTO mensajes (mensaje) VALUES (%s)", (encriptando,))
        db.commit()
        
         # Recoge el correo del destinatario desde el formulario
        recipient_email = request.form.get('email')

        # Enviar el correo electrónico con el archivo .key
        enviar_correo(clave_temporal, recipient_email)
        

        # Pasa el mensaje encriptado a la plantilla HTML
        return render_template('index.html', encrypted_message=encriptando.decode(),BotonyInput=False)
    except Exception as e:
        flask_flash(f"Error al encriptar el mensaje: {str(e)}", 'danger')
        
        # Restablece la clave secreta de Flask a su valor original
        app.secret_key = clave_original
        
        return send_file('index.html')

if __name__ == '__main__':
    # Genera la clave si no exist
    db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="encriptacion"
    )
    cursor = db.cursor()
    cursor.execute('''
     CREATE TABLE IF NOT EXISTS mensajes (
        id INT AUTO_INCREMENT PRIMARY KEY,
        mensaje_encriptado TEXT
     )
     ''')
    if not os.path.exists("Clave.key"):
        genera_Clave()
    app.run(debug=True)
    
@app.teardown_appcontext
def close_db(error):
    cursor.close()
    db.close()
