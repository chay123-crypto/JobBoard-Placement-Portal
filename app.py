from flask import Flask,jsonify,render_template
from flask_login import LoginManager
from models.models import db,User
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.company import company_bp
from celeryset import celery_app
from routes.student import student_bp
from init_db import init
from cache import init_cache
from flask_mail import Mail

manager=LoginManager()
mail=Mail()

def create_app():
    app=Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///portal.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
    app.config['SECRET_KEY']='wxyzab'
    app.config['MAIL_SERVER']='localhost'
    app.config['MAIL_PORT'] =1025
    app.config['MAIL_USE_TLS']=False
    app.config['MAIL_USERNAME']=None
    app.config['MAIL_PASSWORD']=None
    app.config['MAIL_DEFAULT_SENDER']='noreply@placement-portal.com'
    
    init_cache(app)
    
    db.init_app(app)
    with app.app_context():
        init()
    
    @app.route('/')
    def index():
        return render_template('index.html')
    
    mail.init_app(app)

    class TaskContext(celery_app.Task):
        def __call__(self,*args,**kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery_app.Task=TaskContext

    manager.init_app(app)
    @manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    @manager.unauthorized_handler
    def unauthorised():
        return jsonify({'error':'Login Required'}),401
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(company_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(admin_bp)
    return app,mail
    
app,mail=create_app()
if __name__=="__main__":
    app.run(debug=True)
