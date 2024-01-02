from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
  

app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SECRET_KEY'] = 'YourSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:!Qazxsw2@localhost/my_hotel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create the SQLAlchemy db instance
db = SQLAlchemy(app)

 
# Define the data models
class Booking(db.Model):
    __tablename__ = 'booking'
    booking_id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.guest_id'))
    room_number = db.Column(db.String, db.ForeignKey('room.room_number'))
    check_in_date = db.Column(db.Date)
    check_out_date = db.Column(db.Date)
    total_price = db.Column(db.Float)
    booking_date = db.Column(db.Date)

    guest = db.relationship('Guest', backref='bookings')
    room = db.relationship('Room', backref='bookings')


class Guest(db.Model):
    __tablename__ = 'guest'
    guest_id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String)
    contact_info = db.Column(db.String)
  
  
class Room(db.Model):
    __tablename__ = 'room'
    room_number = db.Column(db.String, primary_key=True)
    room_type = db.Column(db.String)
    price_per_night = db.Column(db.Float)
    max_guests = db.Column(db.Integer)


# Route to show the booking list
@app.route('/')
def index():
    return render_template('index.html')
  

# Route to show the booking list
@app.route('/bookings')
def bookings():
    bookings = Booking.query.all()
    return render_template('bookings.html', bookings=bookings)


if __name__ == '__main__':
    app.run(debug=True)
