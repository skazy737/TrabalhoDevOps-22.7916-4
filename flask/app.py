import time
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import ModelView
from sqlalchemy.exc import OperationalError
from prometheus_flask_exporter import PrometheusMetrics
import logging

app = Flask(__name__)

metrics = PrometheusMetrics(app)
app.config['SECRET_KEY'] = 'super_secret_key_1234'

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root_password@mariadb/school_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
appbuilder = AppBuilder(app, db.session)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SchoolApp")

class Aluno(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(50), nullable=False)
    sobrenome = db.Column(db.String(50), nullable=False)
    turma = db.Column(db.String(50), nullable=False)
    disciplinas = db.Column(db.String(200), nullable=False)
    ra = db.Column(db.String(200), nullable=False)

def configurar_banco():
    tentativas = 5
    for tentativa in range(tentativas):
        try:
            with app.app_context():
                db.create_all()  # Criação das tabelas no banco de dados
                # Adiciona um usuário administrador padrão se não existir
                if not appbuilder.sm.find_user(username='admin'):
                    appbuilder.sm.add_user(
                        username='admin',
                        first_name='Admin',
                        last_name='User',
                        email='admin@admin.com',
                        role=appbuilder.sm.find_role(appbuilder.sm.auth_role_admin),
                        password='admin'
                    )
            logger.info("Banco de dados configurado com sucesso!")
            break
        except OperationalError:
            if tentativa < tentativas - 1:
                logger.warning(f"Falha ao conectar ao banco. Tentando novamente ({tentativa + 1}/{tentativas})...")
                time.sleep(5)
            else:
                logger.error("Não foi possível conectar ao banco após várias tentativas.")
                raise

configurar_banco()

class AlunoView(ModelView):
    datamodel = SQLAInterface(Aluno)
    list_columns = ['id', 'nome', 'sobrenome', 'turma', 'disciplinas', 'ra']

appbuilder.add_view(
    AlunoView,
    "Gerenciar Alunos",
    icon="fa-folder-open-o",
    category="Gestão Escolar",
)

@app.route('/alunos', methods=['GET'])
def obter_alunos():
    """Retorna a lista de alunos."""
    lista_alunos = Aluno.query.all()
    resultado = [
        {
            'id': aluno.id,
            'nome': aluno.nome,
            'sobrenome': aluno.sobrenome,
            'turma': aluno.turma,
            'disciplinas': aluno.disciplinas,
            'ra': aluno.ra,
        }
        for aluno in lista_alunos
    ]
    return jsonify(resultado)


@app.route('/alunos', methods=['POST'])
def criar_aluno():
    """Cria um novo aluno."""
    dados = request.get_json()
    novo_aluno = Aluno(
        nome=dados.get('nome'),
        sobrenome=dados.get('sobrenome'),
        turma=dados.get('turma'),
        disciplinas=dados.get('disciplinas'),
        ra=dados.get('ra'),
    )
    db.session.add(novo_aluno)
    db.session.commit()
    logger.info(f"Novo aluno cadastrado: {dados.get('nome')} {dados.get('sobrenome')}")
    return jsonify({'mensagem': 'Aluno cadastrado com sucesso!'}), 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
