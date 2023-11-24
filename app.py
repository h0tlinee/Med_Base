import time
from flask import Flask, render_template, request, flash, redirect, url_for
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

items_info=[{'code':'1','price':'100','description':'good','structure':'hz'},
            {'code':'2','price':'200','description':'good1','structure':'hz1'},
            {'code':'3','price':'300','description':'good2','structure':'hz2'}
            
            
            ]



@app.route('/')
def main():
    return render_template('main.html',
        item_info=items_info            
    )

    
if __name__ == "__main__":
    app.run(debug=True)
