import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import app  

@pytest.fixture
def cliente():
    """Cria um cliente de teste para a aplicação."""
    with app.test_client() as cliente:
        yield cliente

def testar_obter_alunos(cliente: FlaskClient):
    """Verifica a funcionalidade da rota GET /alunos."""
    resposta = cliente.get('/alunos')
    assert resposta.status_code == 200
    assert isinstance(resposta.json, list) 

def testar_criar_aluno(cliente: FlaskClient):
    """Verifica a funcionalidade da rota POST /alunos."""
    aluno_exemplo = {
        "nome": "Ana",
        "sobrenome": "Pereira",
        "turma": "2B",
        "disciplinas": "Química, Biologia",
        "ra": "67890"
    }
    resposta = cliente.post('/alunos', json=aluno_exemplo)
    assert resposta.status_code == 201
    assert resposta.json['mensagem'] == 'Aluno cadastrado com sucesso!'
