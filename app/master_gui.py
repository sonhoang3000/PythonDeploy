import sys

if sys.platform not in ("emscripten", "wasi"):
    from flask import Flask, render_template, request, redirect, url_for, send_from_directory
    from pymongo import MongoClient
    import os

    app = Flask(__name__)

    # Kết nối MongoDB
    client = MongoClient("mongodb+srv://vuhoangson3000:123456789Son@cluster0.we2k3.mongodb.net/")
    db = client["user_database"]
    users_collection = db["users"]

    @app.route("/")
    def index():
        return redirect(url_for("login"))

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = users_collection.find_one({"username": username, "password": password})
            if user:
                return redirect(url_for("game"))  # Chuyển đến trang trò chơi sau khi đăng nhập
            else:
                return "Login failed. Invalid username or password."
        return render_template("login.html")

    @app.route("/register", methods=["GET", "POST"])
    def register():
        if request.method == "POST":
            username = request.form["reg_username"]
            password = request.form["reg_password"]
            email = request.form["reg_email"]
            if users_collection.find_one({"username": username}):
                return "Username already exists. Please choose another."
            users_collection.insert_one({"username": username, "password": password, "email": email})
            return redirect(url_for("login"))
        return render_template("register.html")

    BUILD_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "build/web")

    @app.route("/game")
    def game():
        # return redirect("http://localhost:8000")   
        return render_template("game.html")


    if __name__ == "__main__":
        app.run(host="0.0.0.0", debug=True, port=4000)
