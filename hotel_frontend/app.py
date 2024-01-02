from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
app.config['SECRET_KEY'] = 'YourSecretKey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:PRO6543210@localhost/my_hotel'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Example room data (in a real application, this would come from a database)
rooms = [
    ('101', 'Exquisite Haven'),
    ('102', 'Serene Wave Retreat'),
    ('103', 'Homely Seasons Retreat')
]
class Guest(db.Model):
    guest_id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(255), nullable=False)
    contact_info = db.Column(db.String(255))

class Room(db.Model):
    room_number = db.Column(db.String(10), primary_key=True)
    # other room fields...

class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    guest_id = db.Column(db.Integer, db.ForeignKey('guest.guest_id'), nullable=False)
    room_number = db.Column(db.Integer, db.ForeignKey('room.room_number'), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    # other booking fields...
class BookingForm(FlaskForm):
    guest_name = StringField('Guest Name', validators=[DataRequired()])
    room_number = SelectField('Room Number', choices=rooms, validators=[DataRequired()])
    check_in_date = DateField('Check-In Date', format='%Y-%m-%d', validators=[DataRequired()])
    check_out_date = DateField('Check-Out Date', format='%Y-%m-%d', validators=[DataRequired()])
    contact_info = StringField('Contact Information', validators=[DataRequired()])
    submit = SubmitField('Book Now')

@app.route('/')
def index():
    conn = psycopg2.connect(dbname='my_hotel', user='postgres', password='PRO6543210', host='localhost')
    cur = conn.cursor()
    cur.execute('SELECT check_in_date, check_out_date, guest_id FROM Booking ORDER BY check_in_date;')
    data = cur.fetchall()
    new_data = []
    for row in data:
        new_row = list(row)
        cur.execute(
            f'SELECT guest_name FROM Guest WHERE guest_id = {row[2]}',
        )
        new_row.append(cur.fetchall()[0][0])
        cur.execute(
            f'SELECT contact_info FROM Guest WHERE guest_id = {row[2]}',
        )
        new_row.append(cur.fetchall()[0][0])
        new_data.append(new_row)

    cur.close()
    conn.close()
    return render_template('index.html', data=new_data)


@app.route('/booking', methods=['GET', 'POST'])
def booking():
    form = BookingForm()
    if form.validate_on_submit():
        new_guest = Guest(guest_name=form.guest_name.data, contact_info=form.contact_info.data)
        db.session.add(new_guest)
        db.session.flush()  # Flush to get the ID of the new guest

        checkindate = str(form.check_in_date.data.year) + str(form.check_in_date.data.month) + str(form.check_in_date.data.day)
        checkoutdate = str(form.check_out_date.data.year) + str(form.check_out_date.data.month) + str(form.check_out_date.data.day)
        if checkindate < checkoutdate:
            new_booking = Booking(
                guest_id = new_guest.guest_id,
                room_number = form.room_number.data,
                check_in_date = form.check_in_date.data,
                check_out_date = form.check_out_date.data
            )

            db.session.add(new_booking)
            db.session.commit()
            return redirect(url_for('index'))
        else:
            return render_template('error.html',message ="Reason:Check-in date must be earlier than the check-out date.")
            

    
    return render_template('booking.html', form=form)

@app.route('/accessmap')
def accessmap():
    return render_template('accessmap.html')

@app.route('/sea_house')
def sea_house():
    return render_template('sea_house.html')

@app.route('/normal_four')
def normal_four():
    return render_template('normal_four.html')

@app.route('/Exquisite_Haven')
def Exquisite_Haven():
    return render_template('Exquisite_Haven.html')
if __name__ == '__main__':
    app.run(debug=True)
