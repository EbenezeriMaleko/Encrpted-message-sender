from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.encryption_utilis import encrypt_message, generate_keys
import requests

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://djangouser:Msebenze%40123@localhost/secure_db'
    app.config['SECRET_KEY'] = 'your-secret-key'
    db.init_app(app)

    # Generate keys once (in a real-world app, keys should be securely managed and loaded from a file or database)
    private_key, public_key = generate_keys()

    @app.route('/')
    def home():
        return render_template('sender.html')

    @app.route('/sender', methods=['POST'])
    def sender():
        # Get JSON data from the client
        data = request.json
        message = data.get('message')
        receiver_ip = data.get('receiver_ip')
        receiver_public_key = data.get('receiver_public_key')

        # Ensure the receiver's public key is in byte format
        if isinstance(receiver_public_key, str):  # If the key is a string, encode it to bytes
            receiver_public_key = receiver_public_key.encode('utf-8')

        # Encrypt the message using the receiver's public key
        try:
            encrypted_message = encrypt_message(receiver_public_key, message)

            # Send the encrypted message to the receiver's endpoint
            response = requests.post(
                f"{receiver_ip}/receiver",  # Replace with receiver's endpoint
                json={'encrypted_message': encrypted_message.hex()}  # Convert to hex for transmission
            )
            return jsonify({'status': 'success', 'receiver_response': response.json()})
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)})

    return app