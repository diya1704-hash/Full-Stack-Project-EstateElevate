import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)
app.secret_key = 'flipr_ultra_secret'

# Database Config (Update with your credentials)
# Use environment variables for production
# Updated Database Config in app.py
# Database Configuration for Aiven
app.config['MYSQL_HOST'] = 'mysql-608471f-diyaramawat17-b50b.k.aivencloud.com'
app.config['MYSQL_USER'] = 'avnadmin'
import os
# Use 'AVNS_...' as a backup for local testing, but look for the environment variable first
app.config['MYSQL_PASSWORD'] = os.environ.get('MYSQL_PASSWORD', 'AVNS_T820t72lxjaujRHWlrc')
app.config['MYSQL_DB'] = 'defaultdb'
app.config['MYSQL_PORT'] = 16633

# This is the "Secret Sauce" for Aiven - SSL is REQUIRED
import os
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['MYSQL_CUSTOM_OPTIONS'] = {
    "ssl": {
        "ca": os.path.join(basedir, "ca.pem")
    }
}

mysql = MySQL(app)

def save_and_crop(file, subfolder):
    """Crops image to 450x350 ratio and saves it"""
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
        
        # Calculate cropping
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
    cur = mysql.connection.cursor()
    # Fetch Counts for Dashboard Cards
    cur.execute("SELECT COUNT(*) FROM contact_submissions")
    lead_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM subscribers")
    sub_count = cur.fetchone()[0]
    
    # Fetch Table Data
    cur.execute("SELECT * FROM contact_submissions ORDER BY submitted_at DESC")
    leads = cur.fetchall()
    cur.execute("SELECT * FROM subscribers")
    subs = cur.fetchall()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()
    cur.close()
    
    return render_template('admin.html', leads=leads, subs=subs, 
                           projects=projects, clients=clients,
                           lead_count=lead_count, sub_count=sub_count)

@app.route('/admin/add_project', methods=['POST'])
def add_project():
    img_path = save_and_crop(request.files['image'], 'projects')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO projects (name, description, image_path) VALUES (%s, %s, %s)", 
                (request.form['name'], request.form['desc'], img_path))
    mysql.connection.commit()
    return redirect(url_for('admin'))

@app.route('/admin/add_client', methods=['POST'])
def add_client():
    img_path = save_and_crop(request.files['image'], 'clients')
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO clients (name, description, designation, image_path) VALUES (%s, %s, %s, %s)", 
                (request.form['name'], request.form['desc'], request.form['designation'], img_path))
    mysql.connection.commit()
    return redirect(url_for('admin'))

# Main Landing Page Route
@app.route('/')
def index():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()
    cur.close()
    return render_template('index.html', projects=projects, clients=clients)

if __name__ == '__main__':
    app.run(debug=True)