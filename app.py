from flask import Flask
from config import Config
from models import db
from routes import bp
from flask_login import LoginManager
from models import Usuario

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.login_view = 'main.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    @app.template_filter('formatar_tempo')
    def formatar_tempo_filter(horas):
        """Converte horas decimais em formato 'X horas e Y minutos'. Ex: 3.7 -> '3 horas e 42 minutos'"""
        if horas is None:
            return 'N/A'
        h = int(horas)
        min_ = round((horas - h) * 60)
        if h == 0:
            return f"{min_} minuto" if min_ == 1 else f"{min_} minutos"
        hStr = f"1 hora" if h == 1 else f"{h} horas"
        if min_ == 0:
            return hStr
        minStr = f"1 minuto" if min_ == 1 else f"{min_} minutos"
        return f"{hStr} e {minStr}"

    app.register_blueprint(bp)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Inicializa o db se não existir
        db.create_all()
    app.run(debug=True, port=5000)
