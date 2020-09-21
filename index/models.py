from index import db, login_manager
from flask_login import UserMixin
 
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

 
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key = True)
    firstname = db.Column(db.String(20), unique=True, nullable=False)
    lastname = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(20), unique=True, nullable=False)
    college = db.Column(db.String(20), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.firstname}', '{self.email}', '{self.image_file}')"
