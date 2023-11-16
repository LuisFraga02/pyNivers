from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import date, datetime
import os

app = Flask(__name__, template_folder='templates')
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'amigos.sqlite3')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + db_path
db = SQLAlchemy(app)


class Amigo(db.Model):
    id = db.Column('id', db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(100))
    nascimento = db.Column(db.String(10))

    def __init__(self, nome, nascimento):
        self.nome = nome
        self.nascimento = nascimento


def arrumaData(nascimento):
    # Convert string to datetime object
    date_obj = datetime.strptime(nascimento, "%Y-%m-%d")

    # Format the datetime object as dd/mm/yyyy
    formatted_date = date_obj.strftime("%d/%m/%Y")

    return formatted_date


def aniversario(nascimento):
    nascimento = datetime.strptime(nascimento, "%Y-%m-%d").date()
    data_atual = date.today()
    data_aniversario = nascimento.replace(year=data_atual.year)
    if data_aniversario < data_atual:
        data_aniversario = data_aniversario.replace(year=data_atual.year + 1)
    diferenca = data_aniversario - data_atual
    meses = diferenca.days // 30
    return diferenca.days, meses


def proximoAniversario():
    amigos = Amigo.query.all()
    if amigos:
        amigo_proximo = amigos[0]
        for amigo in amigos:
            if aniversario(amigo.nascimento)[0] < aniversario(amigo_proximo.nascimento)[0]:
                amigo_proximo = amigo
        nome = amigo_proximo.nome
        dias = aniversario(amigo_proximo.nascimento)[0]
        nascimento = amigo_proximo.nascimento
        return nome, dias, nascimento
    else:
        return "Nenhum amigo cadastrado", 0, "2000-01-01"


def aniversaiosNoMes():
    amigos = Amigo.query.all()
    aniversariantes = []
    nomesAniversariantes = []
    stringAniversariantes = ""
    for pessoa in amigos:
        if int(pessoa.nascimento[5:7]) == date.today().month:
            aniversariantes.append(pessoa)
            nomesAniversariantes.append(pessoa.nome)
    quantidade = len(aniversariantes)
    for nome in nomesAniversariantes:
        stringAniversariantes = stringAniversariantes + nome + ", "
    # corta a ultima virgula e espaço da string
    stringAniversariantes = stringAniversariantes[:-2]
    return stringAniversariantes, quantidade


def aniversarioDeAlguem():
    amigos = Amigo.query.all()
    for amigo in amigos:
        if aniversario(amigo.nascimento)[0] == 0:
            return "background-image: url('static/confetti.gif');"

#calcular a idade do amigo
def idade(nascimento):
    nascimento = datetime.strptime(nascimento, "%Y-%m-%d").date()
    data_atual = date.today()
    idade = data_atual.year - nascimento.year - \
        ((data_atual.month, data_atual.day) <
            (nascimento.month, nascimento.day))
    return idade


# coisas pra passar para o html
coisas = {
    "hoje": date.today().strftime('%d/%m/%Y'),
    "arrumaData": arrumaData,
    "aniversario": aniversario,
    "proximoAniversario": proximoAniversario,
    "aniversaiosNoMes": aniversaiosNoMes,
    "aniversarioDeAlguem": aniversarioDeAlguem,
    "idade": idade
}


@app.route('/')
def paginaHome():
    amigos = Amigo.query.all()
    #amigos em ordem que vão fazer aniversário
    amigos = sorted(amigos, key=lambda amigo: aniversario(amigo.nascimento)[0])
    
    return render_template('home.html', amigos=amigos, coisas=coisas)

# rota para adicionar um amigo


@app.route('/adicionar', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        amigo = Amigo(request.form['nome'], request.form['nascimento'])
        db.session.add(amigo)
        db.session.commit()
        return redirect(url_for('paginaHome'))
    return render_template('addAmigo.html', coisas=coisas)

# rota para excluir um amigo


@app.route('/excluir/<int:id>')
def excluir(id):
    amigo = Amigo.query.get(id)
    db.session.delete(amigo)
    db.session.commit()
    return redirect(location=url_for('paginaHome'))

# rota para editar um amigo


@app.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    amigo = Amigo.query.get(id)
    if request.method == 'POST':
        amigo.nome = request.form['nome']
        amigo.nascimento = request.form['nascimento']
        db.session.commit()
        return redirect(url_for('paginaHome'))
    return render_template('editAmigo.html', amigo=amigo, coisas=coisas)


# função rodar o app
if __name__ == '__main__':  # se o arquivo for executado diretamente
    with app.app_context():
        db.create_all()
    # app.run(debug=True) pra rodar em modo debug (pra ver os erros)
    os.system('start http://127.0.0.1:5000/')
    app.run()
