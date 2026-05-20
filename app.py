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

    app.register_blueprint(bp)

    return app

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # Inicializa o db se não existir
        db.create_all()
    app.run(debug=True, port=5000)
