import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pymysql # Changed: Using pymysql for Vercel
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = 'flipr_ultra_secret'
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Database Configuration
MYSQL_HOST = 'mysql-608471f-diyaramawat17-b50b.k.aivencloud.com'
MYSQL_USER = 'avnadmin'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'AVNS_T820t72lxjaujRHWlrc')
MYSQL_DB = 'defaultdb'
MYSQL_PORT = 16633

# Minimal change: This creates a 'mysql' object that behaves like your old one
class MySQLWrapper:
    @property
    def connection(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        conn = pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            ssl={'ca': os.path.join(basedir, "ca.pem")},
            autocommit=True # Ensures data is saved immediately
        )
        return conn

mysql = MySQLWrapper()

def save_and_crop(file, subfolder):
    target_path = os.path.join(app.config['UPLOAD_FOLDER'], subfolder)
    if not os.path.exists(target_path):
        os.makedirs(target_path)
    filename = secure_filename(file.filename)
    full_path = os.path.join(target_path, filename)
    file.save(full_path)
    with Image.open(full_path) as img:
        img = img.convert('RGB')
        target_w, target_h = 450, 350
        width, height = img.size
        target_ratio = target_w / target_h
        current_ratio = width / height
        if current_ratio > target_ratio:
            new_width = int(target_ratio * height)
            offset = (width - new_width) / 2
            img = img.crop((offset, 0, width - offset, height))
        else:
            new_height = int(width / target_ratio)
            offset = (height - new_height) / 2
            img = img.crop((0, offset, width, height - offset))
        img = img.resize((target_w, target_h), Image.Resampling.LANCZOS)
        img.save(full_path)
    return f'uploads/{subfolder}/{filename}'

@app.route('/admin')
def admin():
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM contact_submissions")
    lead_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM subscribers")
    sub_count = cur.fetchone()[0]
    cur.execute("SELECT * FROM contact_submissions ORDER BY submitted_at DESC")
    leads = cur.fetchall()
    cur.execute("SELECT * FROM subscribers")
    subs = cur.fetchall()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('admin.html', leads=leads, subs=subs, 
                           projects=projects, clients=clients,
                           lead_count=lead_count, sub_count=sub_count)

@app.route('/admin/add_project', methods=['POST'])
def add_project():
    img_path = save_and_crop(request.files['image'], 'projects')
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (name, description, image_path) VALUES (%s, %s, %s)", 
                (request.form['name'], request.form['desc'], img_path))
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/add_client', methods=['POST'])
def add_client():
    img_path = save_and_crop(request.files['image'], 'clients')
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name, description, designation, image_path) VALUES (%s, %s, %s, %s)", 
                (request.form['name'], request.form['desc'], request.form['designation'], img_path))
    conn.close()
    return redirect(url_for('admin'))

@app.route('/')
def index():
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', projects=projects, clients=clients)

if __name__ == '__main__':
    app.run(debug=True)