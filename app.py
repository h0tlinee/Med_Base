import time
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

@app.route('/')
def main():
    return render_template('main.html')
    
    
if __name__ == "__main__":
    app.run(debug=True)
