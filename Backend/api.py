from flask import Flask, request, jsonify
from flask_restful import Resource, Api, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import sqlite3
import string
import re
import random
app = Flask(__name__)
api = Api(app)

# *database configuration ->

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sqlite.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def db_connection():
    conn = None
    try:
        conn = sqlite3.connect('instance/sqlite.db')
    except sqlite3.error as e:
        print(e)
    return conn

class SignUpInfo(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(200))
    password = db.Column(db.String(500))
    

class city_table(db.Model):
    city_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    city = db.Column(db.String(200), nullable=False)
        

class bus_table(db.Model):
    bus_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    bus_name = db.Column(db.String(200), nullable=False)
    bus_route = db.Column(db.String(500), nullable=False)
    weekdays = db.Column(db.Integer, nullable=False)
    capacity = db.Column(db.Integer, nullable=False)
    time = db.Column(db.String(500), nullable=False)


class booking_table(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=False)
    bus_id = db.Column(db.Integer, nullable=False)
    source_city = db.Column(db.String(200), nullable=False)
    destination_city = db.Column(db.String(200), nullable=False)
    no_of_tickets_booked = db.Column(db.Integer, nullable=False)
    date = db.Column(db.String(200), nullable=False)


class bus_seat_booking_with_date_table(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(db.Integer, nullable=False)
    bus_id = db.Column(db.Integer, nullable=False)
    booked_seats = db.Column(db.Integer, nullable=False)
    booking_date = db.Column(db.String(20), nullable=False)

class ratings_table(db.Model):
    bus_id = db.Column(db.Integer, primary_key=True)
    no_of_users_rated = db.Column(db.Integer, nullable=False)
    overall_rating = db.Column(db.Float, nullable=False)


class already_rated(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True)
    is_booking_id_already_rated = db.Column(db.Integer, nullable=False)


class offers_table(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    coupon_code = db.Column(db.String(200), nullable=False)
    discount_percentage = db.Column(db.Float, nullable=False)
    min_amount_to_be_spent = db.Column(db.Integer, nullable=False)


#with app.app_context():
 #   db.create_all()

###########################################   Sign Up Info   ######################################################

task_post_args = reqparse.RequestParser()
task_post_args.add_argument('email', type = str, help="Email is Required", required = True)
task_post_args.add_argument('password', type = str, help = "Password is Required", required = True)



resource_fields = {
    'id': fields.Integer,
    'email': fields.String,
    'password': fields.String,
}


class UserInfoList(Resource):
    def get(self):
        tasks = SignUpInfo.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"email": task.email, "password": task.password}
        return todos
    

class UserInfo(Resource):
    @marshal_with(resource_fields)
    def post(self, email):
        args = task_post_args.parse_args()
        task = SignUpInfo.query.filter_by(email = email).first()
        if task:
            abort(409, message = "User Id exists")
        
        todo = SignUpInfo(email = args['email'], password = args['password'])
        db.session.add(todo)
        db.session.commit()
        return todo, 200 
    
    @marshal_with(resource_fields)
    def delete(self, user_id):
       task = SignUpInfo.query.filter_by(id = user_id).first()
       db.session.delete(task)
       db.session.commit()
       return 'User_Id Deleted', 204

class check_email(Resource):
    def get(self, email):
        password = request.args.get('password')
        tasks = SignUpInfo.query.filter_by(email = email).first()
        #<email?password>
        if tasks != None:
            if tasks.password == password:
                return {"email": True, "password": True}
            else:
                return {"email": True, "password": False}
        else:
            return {"email": False, "password": False}
        
        
        
        
#####################################################   CITY  ########################################################


resource_fields = {
    'id': fields.Integer,
    'city_id': fields.String,
}

city_post_args = reqparse.RequestParser()
city_post_args.add_argument('city', type = str, help="City is Required", required = True)

class City_List(Resource):
    def get(self):
        tasks = city_table.query.all()
        todos = {}
        for task in tasks:
            todos[task.id] = {"city": task.city}
        return todos

class City_Manipulate(Resource):
    @marshal_with(resource_fields)
    def post(self, city):
        args = city_post_args.parse_args()
        task = city_table.query.filter_by(city = city).first()
        if task:
            abort(409, message = "City exists")
        
        todo = city_table(city = args['city'])
        db.session.add(todo)
        db.session.commit()
        return todo, 200 
  

    
    
#####################################  BUS  #########################################################################

resource_fields = {
    'bus_id': fields.Integer,
    'bus_name': fields.String,
    'bus_route': fields.String,
    'weekdays': fields.Integer,
    'capacity': fields.Integer,
    'time': fields.String
}


bus_post_args = reqparse.RequestParser()
bus_post_args.add_argument('bus_name', type = str, help="Bus is Required", required = True)
bus_post_args.add_argument('bus_route', type = str, help="Bus Route is Required", required = True)
bus_post_args.add_argument('weekdays', type = int, help="Weekdays are Required", required = True)
bus_post_args.add_argument('capacity', type = int, help="Capacity is Required", required = True)
bus_post_args.add_argument('time', type = str, help="Time is Required", required = True)


class Bus_List(Resource):
    def get(self):
        tasks = bus_table.query.all()
        todos = {}
        for task in tasks:
            todos[task.bus_id] = {"bus_name": task.bus_name, "bus_route": task.bus_route, "weekdays": task.weekdays,
                              "capacity": task.capacity, "time": task.time}
        return todos

class Bus_Manipulate(Resource):
    @marshal_with(resource_fields)
    def post(self):
        # Parse request arguments
        args = bus_post_args.parse_args()
        
        # Create new bus object
        new_bus = bus_table(
            bus_name=args['bus_name'],
            bus_route=args['bus_route'],
            weekdays=args['weekdays'],
            capacity=args['capacity'],
            time=args['time']
        )
        db.session.add(new_bus)
        db.session.commit()






#######################################   BOOKING   ###################################################################


resource_fields = {
    'booking_id': fields.Integer,
    'user_id': fields.Integer,
    'bus_id': fields.Integer,
    'source_city': fields.String,
    'destination_city': fields.String,
    'no_of_tickets_booked': fields.Integer,
    'date': fields.String,
}


booking_post_args = reqparse.RequestParser()
booking_post_args.add_argument('user_id', type = str, help="User_id is Required", required = True)
booking_post_args.add_argument('bus_id', type = str, help="Bus_id Route is Required", required = True)
booking_post_args.add_argument('source_city', type = str, help="Source City is Required", required = True)
booking_post_args.add_argument('destination_city', type = str, help="Destination City is Required", required = True)
booking_post_args.add_argument('no_of_tickets_booked', type = int, help="No of tickets booked is Required", required = True)
booking_post_args.add_argument('date', type = str, help="Date is Required", required=True)


class Booking_List(Resource):
    def get(self):
        tasks = booking_table.query.all()
        todos = {}
        for task in tasks:
            todos[task.booking_id] = {"user_id": task.user_id, "bus_id": task.bus_id, "source_city": task.source_city,
                              "destination_city": task.destination_city, "no_of_tickets_booked": task.no_of_tickets_booked,
                              "date": task.date}
        return todos
    

class Booking_Manipulate(Resource):
    @marshal_with(resource_fields)
    def post(self):
        # Parse request arguments
        args = booking_post_args.parse_args()
        
        # Create new bus object
        new_booking = booking_table(
            user_id=args['user_id'],
            bus_id=args['bus_id'],
            source_city=args['source_city'],
            destination_city=args['destination_city'],
            no_of_tickets_booked=args['no_of_tickets_booked'],
            date=args['date']
        )
        db.session.add(new_booking)
        db.session.commit()



@app.route('/search_bus/<source>/<destination>/<weekday>/<date_str>')
def search_bus_final(source, destination, weekday, date_str):
    conn = db_connection()
    cursor = conn.cursor()

    if request.method == 'GET':
        cursor.execute("SELECT bus_name, bus_route, bus_id FROM bus_table WHERE weekdays LIKE ?", ('%' + weekday + '%', ))
        bus_list = cursor.fetchall()

        result = []
        for bus in bus_list:
            bus_stops = re.findall(r'(\w+)\((\d{2}:\d{2})\)-?', bus[1])
            bus_id = bus[2]
            departure_time = None
            arrival_time = None
            seats_available = 50

            for i in range(len(bus_stops)):
                if bus_stops[i][0] == source:
                    departure_time = bus_stops[i][1]
                    for j in range(i+1, len(bus_stops)):
                        if bus_stops[j][0] == destination:
                            arrival_time = bus_stops[j][1]
                            break
                    break

            if departure_time and arrival_time:
                cursor.execute("SELECT SUM(no_of_tickets_booked) FROM booking_table WHERE bus_id=? AND date=?", (bus_id, date_str))
                booked_seats = cursor.fetchone()[0]

                if booked_seats:
                    seats_available = 50 - booked_seats

                print(booked_seats);
                
                result.append({
                    'bus_name': bus[0],
                    'departure_time': departure_time,
                    'arrival_time': arrival_time,
                    'seats_available': seats_available,
                    'date': date_str,
                    'bus_id': bus[2]
                })

        conn.close()
        return jsonify({'bus_routes': result})
    
    
########################################   BUS_BOOK_WITH_DATE ###############################################################
resource_fields = {
    'id': fields.Integer,
    'booking_id': fields.Integer,
    'bus_id': fields.Integer,
    'booked_seats': fields.Integer,
    'booking_date': fields.String,
}

booking_with_date_post_args = reqparse.RequestParser()
booking_with_date_post_args.add_argument('booking_id', type = int, help="booking id is required", required = True)
booking_with_date_post_args.add_argument('bus_id', type = int, help="Bus_id is Required", required = True)
booking_with_date_post_args.add_argument('booked_seats', type = int, help="Booked Seat is required", required = True)
booking_with_date_post_args.add_argument('booking_date', type = str, help="booking date is required", required = True)


class Booking_with_date_Manipulate(Resource):
    @marshal_with(resource_fields)
    def post(self):
        # Parse request arguments
        args = booking_with_date_post_args.parse_args()
        
        # Create new bus object
        new_booking_with_date = bus_seat_booking_with_date_table(
            booking_id=args['booking_id'],
            bus_id=args['bus_id'],
            booked_seats=args['booked_seats'],
            booking_date=args['booking_date']
        )
        db.session.add(new_booking_with_date)
        db.session.commit()




##################################### ratings table #############################################################
resource_fields = {
    'bus_id': fields.Integer,
    'no_of_users_rated': fields.Integer,
    'overall_rating': fields.Float,
}

ratings_table_post_args = reqparse.RequestParser()
ratings_table_post_args.add_argument('bus_id', type = int, help="Bus_id is Required", required = True)
ratings_table_post_args.add_argument('no_of_users_rated', type = int, help="No of users rated is required", required = True)
ratings_table_post_args.add_argument('overall_rating', type = float, help="Overall rating is required", required = True)

class Rating_manipulate(Resource):
    @marshal_with(resource_fields)
    def post(self):
        # Parse request arguments
        args = ratings_table_post_args.parse_args()
        
        # Create new bus object
        new_rating = ratings_table(
            bus_id=args['bus_id'],
            no_of_users_rated=args['no_of_users_rated'],
            overall_rating=args['overall_rating']
        )
        db.session.add(new_rating)
        db.session.commit()



################################### is_booking_id_rated #######################################################
resource_fields = {
    'booking_id': fields.Integer,
    'is_booking_id_already_rated': fields.Integer,
}

already_rated_table_post_args = reqparse.RequestParser()
already_rated_table_post_args.add_argument('booking_id', type = int, help="Booking_id is Required", required = True)
already_rated_table_post_args.add_argument('is_booking_id_already_rated', type = int, help="Booking_id is Required", required = True)

class already_rated_manipulate(Resource):
    @marshal_with(resource_fields)
    def post(self):
        # Parse request arguments
        args = already_rated_table_post_args.parse_args()
        
        # Create new bus object
        new_object = already_rated(
            booking_id=args['booking_id'],
            is_booking_id_already_rated=args['is_booking_id_already_rated'],
        )
        db.session.add(new_object)
        db.session.commit()

#############################################    offers table     ##########################################################

resource_fields = {
    'coupon_code': fields.Integer,
    'discount_percentage': fields.Integer,
    'min_amount_to_be_spent': fields.String,
}

offers_table_post_args = reqparse.RequestParser()
offers_table_post_args.add_argument('coupon_code', type = str, help="coupon_code is Required", required = True)
offers_table_post_args.add_argument('discount_percentage', type = float, help="discount_percentage is Required", required = True)
offers_table_post_args.add_argument('min_amount_to_be_spent', type = int, help="min_amount_to_be_spent is Required", required = True)

class offers_table_manipulate(Resource):
    @marshal_with(resource_fields)
    def post(self):
        # Parse request arguments
        args = offers_table_post_args.parse_args()
        
        # Create new bus object
        new_offer = offers_table(
            coupon_code=args['coupon_code'],
            discount_percentage=args['discount_percentage'],
            min_amount_to_be_spent=args['min_amount_to_be_spent'],
        )
        db.session.add(new_offer)
        db.session.commit()
        
   
   
   
   
   
   
   
        
@app.route('/booking/<int:bus_id>')
def get_booking(bus_id):
    conn = db_connection()
    c = conn.cursor()

    # Retrieve the booked seats for the specified bus_id
    c.execute("SELECT booked_bus_seats_with_date FROM bus_seat_booking_with_date_table WHERE bus_id = ?", (bus_id,))
    booking_data = c.fetchone()[0]

    # Split the booking data into individual booking strings
    booking_strings = booking_data.split(',')

    # Loop through the booking strings and extract the date and seats for each booking
    bookings = []
    for booking_string in booking_strings:
        # Strip the parentheses from the booking string
        booking_string = booking_string.strip('()')

        # Split the booking string into a date and seats
        booking_parts = booking_string.split(':')
        if len(booking_parts) != 2:
            continue  # Skip this booking if it doesn't have a valid date and seats

        date, seats = booking_parts

        # Split the seats string into a list of seat numbers
        seats = seats.split('_')

        # Convert the seats to integers
        seats = [int(seat) for seat in seats]

        # Append the booking to the list of bookings
        bookings.append({'date': date, 'seats': seats})

    # Return the bookings as a JSON response
    return jsonify({'bus_id': bus_id, 'bookings': bookings})



@app.route('/<bus_id>/<date>', methods=['GET'])
def get_booked_seats(bus_id, date):
    #print(bus_name)
    # Connect to the database
    conn = db_connection()
    c = conn.cursor()

    # Query the database to fetch the booked seats
    print(bus_id)
    c.execute("SELECT booked_seats FROM bus_seat_booking_with_date_table WHERE bus_id=? AND booking_date=?", (bus_id, date))
    result = c.fetchall()
    print(result)

    if result:
        return {'booked_seats': result}
    else:
        return {'booked_seats': "0"}
    

@app.route('/<email>', methods=['GET'])
def fetch_user_id(email):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT id FROM sign_up_info WHERE email=(?)", (email,))
    result = c.fetchone()
    
    if result:
        return {'user_id': result}
    else:
        return {'user_no_id': '-1'}
    


@app.route('/fetch_booking_id', methods=['GET'])
def fetch_booking_id():
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT booking_id FROM booking_table WHERE booking_id=(SELECT max(booking_id) FROM booking_table)")
    result = c.fetchone()
    
    if result:
        return {'booking_id': result}
    else:
        return {'booking_no_id': '-1'}
    

@app.route('/fetch_user_bookings/<user_id>', methods=['GET'])
def fetch_user_previous_bookings(user_id):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT booking_id, bus_id, source_city, destination_city, no_of_tickets_booked, date FROM booking_table WHERE user_id=(?)", (user_id,))
    results = c.fetchall()
    print(results)
    answer = []
    for row in results:
        answer.append({
            'booking_id': row[0],
            'bus_id': row[1],
            'source_city': row[2],
            'destination_city': row[3],
            'no_of_tickets_booked': row[4],
            'date': row[5]
        })

    if results:
        return answer
    else:
        return "-1"


@app.route('/fetch_password/<email>', methods=['GET'])
def fetch_user_password(email):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT password FROM sign_up_info WHERE email=(?)", (email,))
    result = c.fetchone()  # fetch a single result tuple
    
    if result:
        # return a dictionary with a single key "password" and the password string as the value
        return {'password': result[0]}
    else:
        # return an error message as a dictionary
        return {'error': 'password not found'}


@app.route('/fetch_bus_name/<bus_id>', methods=['GET'])
def fetch_bus_name(bus_id):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT bus_name FROM bus_table WHERE bus_id=(?)", (bus_id,))
    result = c.fetchall()  # fetch a single result tuple
    
    if result:
        # return a dictionary with a single key "password" and the password string as the value
        return {'bus_name': result[0]}
    else:
        # return an error message as a dictionary
        return {'error': 'bus_name not found'}
    


@app.route('/fetch_rating/<bus_id>', methods=['GET'])
def fetch_rating(bus_id):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT overall_rating FROM ratings_table WHERE bus_id=(?)", (bus_id,))
    result = c.fetchall()  # fetch a single result tuple
    
    if result:
        return {'rating': result[0]}
    else:
        return {'error': 'bus_id not found'}
    



@app.route('/update_rating/<int:bus_id>/<float:rating>', methods=['PUT'])
def update_rating(bus_id, rating):
    # Query the database for the existing rating entry
    rating_entry = ratings_table.query.filter_by(bus_id=bus_id).first()

    # Update the no_of_users_rated, overall_rating, and already_rated fields
    if rating_entry:
        if not rating_entry.already_rated:
            new_no_of_users_rated = rating_entry.no_of_users_rated + 1
            new_overall_rating = round((rating_entry.overall_rating * rating_entry.no_of_users_rated + rating) / new_no_of_users_rated, 1)

            rating_entry.no_of_users_rated = new_no_of_users_rated
            rating_entry.overall_rating = new_overall_rating
            rating_entry.already_rated = True

            db.session.commit()

            return jsonify({'message': f'Rating for bus_id {bus_id} updated successfully'})
        else:
            return jsonify({'message': f'You have already rated bus_id {bus_id}'}), 400
    else:
        return jsonify({'message': f'No rating found for bus_id {bus_id}'}), 404


@app.route('/is_already_rated/<booking_id>', methods=['GET'])
def Is_already_rated(booking_id):
    conn = db_connection()
    c = conn.cursor()
    c.execute("SELECT is_booking_id_already_rated FROM already_rated WHERE booking_id=(?)", (booking_id,))
    result = c.fetchall()  # fetch a single result tuple
    
    if result:
        return {'is_already_rated': '1'}
    else:
        return {'is_already_rated': '0'}



@app.route('/delete_booking/<booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    conn = db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM booking_table WHERE booking_id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return f"Booking with ID {booking_id} has been deleted from the database."



@app.route('/delete_booking_with_date/<booking_id>', methods=['DELETE'])
def delete_booking_with_date(booking_id):
    conn = db_connection()
    c = conn.cursor()
    c.execute("DELETE FROM bus_seat_booking_with_date_table WHERE booking_id = ?", (booking_id,))
    conn.commit()
    conn.close()
    return f"All bookings with ID {booking_id} have been deleted from the database."



@app.route('/fetch_offers', methods=['GET'])
def Fetch_Offers():
    conn = db_connection()
    c = conn.cursor()

    c.execute("SELECT * FROM offers_table")
    results = c.fetchall()
    print(results)
    answer = []
    for row in results:
        answer.append({
            'id': row[0],
            'coupon_code': row[1],
            'discount_percentage': row[2],
            'min_amount_to_be_spent': row[3],
        })

    if results:
        return answer
    else:
        return "-1"
    



@app.route('/check_if_coupon_code_exists/<coupon_code>', methods=['GET'])
def check_coupon(coupon_code):
    conn = db_connection()
    c = conn.cursor()

    c.execute("SELECT discount_percentage, min_amount_to_be_spent FROM offers_table WHERE coupon_code = (?)", (coupon_code, ))
    results = c.fetchall()
    print(results)
    answer = []
    for row in results:
        answer.append({
            'discount_percentage': row[0],
            'min_amount_to_be_spent': row[1],
        })

    if results:
        return answer
    else:
        return "-1"
    


api.add_resource(check_email, '/check/<email>')

api.add_resource(UserInfo, '/signup/<email>')
api.add_resource(UserInfoList, '/signup')

api.add_resource(City_List, '/city')
api.add_resource(City_Manipulate, '/city/<city>')

api.add_resource(Bus_List, '/bus')
api.add_resource(Bus_Manipulate, '/buses')

api.add_resource(Booking_List, '/booking')
api.add_resource(Booking_Manipulate, '/bookings')

api.add_resource(Booking_with_date_Manipulate, '/booking_with_date')

api.add_resource(Rating_manipulate, '/add_rating')

api.add_resource(already_rated_manipulate, '/add_already_rated')

api.add_resource(offers_table_manipulate, '/add_offer')

if(__name__) == '__main__':
    app.run(debug=True)
CORS(app, resources={r"/*": {"origins": "*"}})





