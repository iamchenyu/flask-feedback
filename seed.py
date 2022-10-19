from app import app
from models import db, User, Feedback

with app.app_context():
    db.drop_all()
    db.create_all()

# Add Users
daniel = User.register(username="daneil", password="daniel123",
                       email="dlouise@gmail.com", first_name="Daniel", last_name="Louise", is_admin=True)

stevie = User.register(username="stevie", password="stevie123",
                       email="stevie@gmail.com", first_name="Stevie", last_name="Feliciano")

elliot = User.register(username="elliot", password="elliot123",
                       email="elliot@gmail.com", first_name="Elliot", last_name="Fu")

helen = User.register(username="helen", password="helen123",
                      email="helen@gmail.com", first_name="Helen", last_name="Chris")

with app.app_context():
    db.session.add_all([daniel, stevie, elliot, helen])
    db.session.commit()

# Add Feedback
f1 = Feedback(title="Great!",
              content="I love this website! It is amazing!", user_id=2)

f2 = Feedback(title="Whatever", content="Very mediocare", user_id=4)

f3 = Feedback(title="It sucks!", content="Get me out of here!", user_id=3)

with app.app_context():
    db.session.add_all([f1, f2, f3])
    db.session.commit()
