from datetime import datetime
from flask import Flask, render_template
from flask import jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import extract
from itertools import cycle
app = Flask(__name__)

# Configure the SQLAlchemy part of the app instance
app.config['SECRET_KEY'] = 'YourSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:PRO6543210@localhost/my_hotel'
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

@app.route('/booking_counts_by_month')
def booking_counts_by_month():
    # Extract month from the check-in date and count bookings for each month
    booking_counts_by_month = db.session.query(extract('month', Booking.check_in_date).label('month'),
                                               db.func.count().label('count')).group_by(extract('month', Booking.check_in_date)).all()

    # Create a cycle of months from 1 to 12
    all_months = list(range(1, 13))
    months = []
    counts = []

    # Fill in counts for each month, or set count to 0 if no data
    for month in all_months:
        found = False
        for month_count in booking_counts_by_month:
            if month_count[0] == month:
                months.append(month_count[0])
                counts.append(month_count[1])
                found = True
                break
        if not found:
            months.append(month)
            counts.append(0)

    # Return data as JSON
    return jsonify({
        'months': months,
        'counts': counts
    })
# Route to show the booking list
@app.route('/booking_counts_by_room')
def booking_counts_by_room():
    # Fetch booking counts for each room number from the database
    booking_counts_by_room = db.session.query(Booking.room_number, db.func.count().label('count')).group_by(Booking.room_number).all()

    # Extract room numbers and counts
    room_numbers = [room_count[0] for room_count in booking_counts_by_room]
    counts = [room_count[1] for room_count in booking_counts_by_room]

    # Return data as JSON
    return jsonify({
        'labels': room_numbers,
        'counts': counts
    })  

@app.route('/')
def index():
    return render_template('index.html')
     
       
# Route to show the booking list
@app.route('/bookings')
def bookings():
    bookings = Booking.query.all()
    return render_template('bookings.html', bookings=bookings)
   
  
@app.route('/cancel_booking', methods=['POST'])
def cancel_booking():
    data = request.get_json()
    booking_id = data.get('booking_id')
    print(f"booking_id: {booking_id}")
     
    try:
        booking = Booking.query.get(booking_id)
        if booking:
            db.session.delete(booking)
            db.session.commit()
            return jsonify({"status": "success", "message": "Booking deleted"})
        else:
            return jsonify({"status": "error", "message": "Booking not found"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/update_booking_date', methods=['POST'])
def update_booking_date():
    data = request.get_json()
    booking_id = data['booking_id']
    date_type = data['date_type']
    new_date = data['new_date']
    print(f"booking_id: {booking_id}, date_type: {date_type}, new_date: {new_date}")
    
    try:
        booking = Booking.query.get(booking_id)
        if booking:
            if date_type == 'check_in_date':
                booking.check_in_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            elif date_type == 'check_out_date':
                booking.check_out_date = datetime.strptime(new_date, '%Y-%m-%d').date()
            db.session.commit()
            return jsonify({"status": "success", "message": "Booking date updated"})
        else:
            return jsonify({"status": "error", "message": "Booking not found"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
