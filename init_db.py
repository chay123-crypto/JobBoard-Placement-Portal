from models.models import db,User

def init():
    db.create_all()
    admin=User.query.filter_by(role='admin').first()
    if not admin:
        new_admin=User(email='admin@placement.in',role='admin',contact_no='0000000000')
        new_admin.set_password('admin@123')
        db.session.add(new_admin)
        db.session.commit()
        print("admin created successfully")
    else:
        print("admin exist already")

if __name__ == "__main__":
    from app import create_app
    app=create_app()
    with app.app_context():
        init()