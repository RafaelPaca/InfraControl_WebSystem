from app import create_app
from models import db, Usuario, Setor
from ml_model import train_initial_model
from datetime import date

def seed_data():
    app = create_app()
    with app.app_context():
        db.create_all()
        
        # Cria admin se não existir
        admin = Usuario.query.filter_by(nome='Admin').first()
        if not admin:
            admin = Usuario(
                nome='Admin',
                sobrenome='Sistema',
                cpf='000.000.000-00',
                data_nascimento=date(1990, 1, 1),
                email_corporativo='admin@infracontrol.com',
                perfil='Admin'
            )
            admin.set_senha('infra123')
            db.session.add(admin)
            
        # Cria alguns setores padrão
        setores = [
            'RECEPÇÃO', 'RH', 'ADMINISTRAÇÃO', 'ALMOXARIFADO', 'SETOR DE VENDAS', 
            'SETOR DE TI', 'SANITÁRIO MASCULINO - TÉRREO', 'SANITÁRIO FEMININO - TÉRREO', 
            'CORREDOR TÉRREO', 'ESTACIONAMENTO', 'EXPEDIÇÃO', 'SANITÁRIO MASCULINO - 1° ANDAR', 
            'SANITÁRIO FEMININO - 1° ANDAR', 'CORREDOR 1° ANDAR', 'COPA', 
            'VESTIÁRIO MASCULINO', 'VESTIÁRIO FEMININO', 'OUTRO SETOR/LOCAL'
        ]
        
        for nome in setores:
            if not Setor.query.filter_by(nome=nome).first():
                db.session.add(Setor(nome=nome))
                
        db.session.commit()
        print("Banco de dados populado com sucesso.")
        
        # Treina o modelo ML
        print("Treinando modelo de ML...")
        train_initial_model()

if __name__ == '__main__':
    seed_data()
