from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
SocketIO = SocketIO(app)

#python dict. store connected users. key is socket id value is username and avatarUrl
users = {}

@app.route("/")
def index():
    return render_template("index.html")

#we are listening for the connect event
@SocketIO.on("connect")
def handle_connect():
    username= f"user_{random.randint(1000, 9999)}"
    gender = random.choice(["girl", "boy"])
    #https://avatar.iran.liara.run/public/boy?username=User_123
    avatar_url = f"https://avatar.iran.liara.run/public/{gender}?username={username}"


    users[request.sid] = { "username": username, "avatarUrl": avatar_url }


    emit("user_joined", { "username": username, "avatarUrl": avatar_url}, broadcast=True)


    emit("set_username", { "username": username})



@SocketIO.on("disconnect")
def handle_disconnect():
    user = users.pop(request.sid, None)
    if user:
        emit("user_left", {"username":user["username"]}, broadcast=True)



@SocketIO.on("send_message")
def handle_message(data):
    user = users.get(request.sid)
    if user:
        emit("new_message", {
            "username": user["username"],
            "avatarUrl": user["avatarUrl"],
            "message": data["message"]
        }, broadcast=True)



@SocketIO.on("update_username")
def handle_update_username(data):
    old_username = users[request.sid]["username"]
    new_username = data["username"]
    users[request.sid]["username"] = new_username

    emit("username_updated", {
        "old_username": old_username,
        "new_username": new_username}, broadcast=True)


if __name__ == "__main__":
    SocketIO.run(app, host="0.0.0.0", port=5000)