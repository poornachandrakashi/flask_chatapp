from flask import Flask,render_template,request,redirect,url_for,flash,session
from flask_socketio import SocketIO, join_room
#Using flask-login library
from flask_login import LoginManager, login_user, logout_user,login_required,current_user
from db import *
from pymongo.errors import DuplicateKeyError


app=Flask(__name__)
socketio= SocketIO(app)
login_manager=LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key="poorna1999"

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    message= ""
    if request.method=='POST':
        username= request.form.get('username')
        password_input = request.form.get('password')
        email =  request.form.get('email')
        user = get_user(username)
        try:
            save_user(username,email,password_input)
            return redirect(url_for('login'))
        except DuplicateKeyError:
            message="User already exists"
        
    return render_template('signup.html',message=message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    
    message= ""
    if request.method=='POST':
        username= request.form.get('username')
        password_input = request.form.get('password')
        user = get_user(username)
        
        if user and user.check_password(password_input):
            login_user(user)
            return redirect(url_for('home'))
        
        else:
            message ="Failed to login"
            
    return render_template('login.html',message=message)

@app.route('/create-room',methods=['GET','POST'])
@login_required
def create_room():
    
    if request.method=='POST':
        room_name= request.form.get('room_name')
        usernames=[username.strip() for username in request.form.get('members').split(',')] #Creating a list of username seperated by commos
        
        if len(room_name) and len(usernames):
            room_id=save_room(room_name,current_user.username)
            if current_user.username in usernames:
                usernames.remove(current_user.username)
            add_room_member(room_id,room_name,usernames,current_user.username)
            
        else:
            message = "Failed to create a room"
                
    return render_template('create_room.html')

@app.route('/chat')
def chat():
    username=request.args.get('username')
    room=request.args.get('room')
    
    if username and room:
        return render_template('chat.html',username=username,room=room)
    else:
        redirect(url_for('home'))
        
@socketio.on('send_message')
def handle_send_message_event(data):
    app.logger.info("{} has sent message to the room {}:{}".format(data['username'], data['room'],data['message']))  
    
    socketio.emit('receive_message',data,room=data['room'])    


@socketio.on('join_room')
def handle_join_room_event(data): 
    app.logger.info("{} has joined the room {}".format(data['username'], data['room']))

# which all rooms
    join_room(data['room'])
    #which will send a announcement that someone has joined the event
    socketio.emit('join_room_announcement',data)
    
@login_manager.user_loader
def load_user(username):
    return get_user(username)

# Check if user logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__=="__main__":
    socketio.run(app, debug=True)