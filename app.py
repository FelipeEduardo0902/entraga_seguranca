from flask import Flask, make_response, jsonify, request, render_template, redirect, url_for
import mysql.connector
from flask_wtf import CSRFProtect
from markupsafe import escape
from dotenv import load_dotenv
import os

# Carrega as variáveis do .env
load_dotenv()

# Configurações do Flask
app = Flask(__name__, static_folder='static')
app.config['JSON_SORT_KEYS'] = False
app.config['SECRET_KEY'] = 'd0cketT0p'
csrf = CSRFProtect(app)

# Obtém as informações do banco do .env
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# Configura a conexão com o banco de dados
mydb = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)

# Listagem de currículos
@app.route('/')
def index():
    my_cursor = mydb.cursor()
    my_cursor.execute('SELECT id, nome, email FROM curriculos')
    curriculos = my_cursor.fetchall()
    return render_template('index.html', curriculos=curriculos)

# Cadastro de currículo
@app.route('/cadastro', methods=['GET', 'POST'])
@csrf.exempt
def create_curriculo():
    if request.method == 'POST':
        # Captura e sanitiza os dados enviados pelo formulário
        nome = escape(request.form.get('nome'))
        telefone = escape(request.form.get('telefone'))
        email = escape(request.form.get('email'))
        endereco_fisico = escape(request.form.get('endereco_fisico'))
        experiencia = escape(request.form.get('experiencia'))

        errors = {}

        # Validações 
        if not nome:
            errors['nome'] = "O campo nome é obrigatório."
        if not email:
            errors['email'] = "O campo email é obrigatório."
        if not experiencia:
            errors['experiencia'] = "O campo experiência profissional é obrigatório."

        # Validação e-mail
        import re
        if email and not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
            errors['email'] = "O e-mail fornecido é inválido."

        # Validação do telefone (somente números, entre 10 e 15 dígitos)
        if telefone and not re.match(r"^\d{10,12}$", telefone):
            errors['telefone'] = "O telefone deve conter entre 10 e 12 números."

        # Se houver erros, renderiza a página de cadastro com os erros e dados preenchidos
        if errors:
            return render_template(
                'cadastro.html',
                errors=errors,
                nome=nome,
                telefone=telefone,
                email=email,
                endereco_fisico=endereco_fisico,
                experiencia=experiencia
            )

        # Insere os dados no banco se não houver erros
        my_cursor = mydb.cursor()
        sql = "INSERT INTO curriculos (nome, telefone, email, endereco_fisico, experiencia) VALUES (%s, %s, %s, %s, %s)"
        val = (nome, telefone, email, endereco_fisico, experiencia)
        my_cursor.execute(sql, val)
        mydb.commit()

        return redirect(url_for('index'))

    # Renderiza a página de cadastro para requisições GET
    return render_template('cadastro.html')

# Consulta de currículo
@app.route('/curriculo/<int:id>')
def view_curriculo(id):
    my_cursor = mydb.cursor()
    sql = "SELECT * FROM curriculos WHERE id = %s"
    my_cursor.execute(sql, (id,))
    curriculo = my_cursor.fetchone()
    
    if not curriculo:
        return make_response(jsonify(mensagem="Currículo não encontrado"), 404)

    return render_template('consulta.html', curriculo=curriculo)

# Exclusão de currículo
@app.route('/curriculo/<int:id>/delete', methods=['POST'])
@csrf.exempt
def delete_curriculo(id):
    my_cursor = mydb.cursor()
    sql = "SELECT * FROM curriculos WHERE id = %s"
    my_cursor.execute(sql, (id,))
    curriculo = my_cursor.fetchone()

    # Verifica se o currículo existe
    if not curriculo:
        return make_response(jsonify(mensagem="Currículo não encontrado"), 404)

    # Exclui o currículo
    sql = "DELETE FROM curriculos WHERE id = %s"
    my_cursor.execute(sql, (id,))
    mydb.commit()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
