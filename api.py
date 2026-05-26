@ -1,29 +0,0 @@
﻿from flask import Flask, request, jsonify
import re

app = Flask(__name__)

@app.route('/api/validar-email', methods=['POST'])
def validar_email():
    data = request.get_json()
    email = data.get('email', '')
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    valido = bool(re.match(patron, email))
    return jsonify({
        'email': email,
        'valido': valido,
        'mensaje': 'Email válido' if valido else 'Email inválido'
    })

@app.route('/api/excel/sumar', methods=['POST'])
def excel_sumar():
    data = request.get_json()
    numeros = data.get('numeros', [])
    return jsonify({'suma': sum(numeros), 'cantidad': len(numeros)})

@app.route('/', methods=['GET'])
def home():
    return jsonify({'mensaje': 'API funcionando', 'endpoints': ['/api/validar-email', '/api/excel/sumar']})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
@ -1,3 +1,4 @@
@ -1,29 +0,0 @@
﻿from flask import Flask, request, jsonify
import re

