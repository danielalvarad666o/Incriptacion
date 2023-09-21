from flask import Flask, request, render_template, send_file, flash as flask_flash
from cryptography.fernet import Fernet
import os
import mysql.connector

app = Flask(__name__)

# Funciones para manejar la encriptación

def genera_Clave():
    clave = Fernet.generate_key()
    with open("Clave.key", "wb") as archivo_clave:
        archivo_clave.write(clave)

def cargar_clave():
    return open("Clave.key", "rb").read()

# Configura la clave secreta de Flask utilizando la clave generada
app.secret_key = cargar_clave()

@app.route('/')
def index():
    return render_template('index.html', encrypted_message=" ")

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
        cursor.execute("INSERT INTO mensajes (mensaje_encriptado) VALUES (%s)", (encriptando,))
        db.commit()
        cursor.close()
        db.close()

        # Pasa el mensaje encriptado a la plantilla HTML
        return render_template('index.html', encrypted_message=encriptando.decode())
    except Exception as e:
        flask_flash(f"Error al encriptar el mensaje: {str(e)}", 'danger')
        
        # Restablece la clave secreta de Flask a su valor original
        app.secret_key = clave_original
        
        return send_file('index.html')

if __name__ == '__main__':
    # Genera la clave si no existe
    

    db = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="encrypt"
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
