import os
import pymysql
import base64
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'flipr_ultra_secret'

# --- Database Configuration ---
MYSQL_HOST = 'mysql-608471f-diyaramawat17-b50b.k.aivencloud.com'
MYSQL_USER = 'avnadmin'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'AVNS_T820t72lxjaujRHWlrc')
MYSQL_DB = 'defaultdb'
MYSQL_PORT = 16633

class MySQLWrapper:
    def get_conn(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        return pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            ssl={'ca': os.path.join(basedir, "ca.pem")},
            autocommit=True,
            # CRITICAL: DictCursor allows us to access data like p['name'] in HTML
            cursorclass=pymysql.cursors.DictCursor 
        )

mysql = MySQLWrapper()

# --- Helper Function for Image Processing ---
def get_base64_image(file):
    """Converts an uploaded file into a Base64 string for DB storage."""
    if file and file.filename != '':
        # Read the file and encode it to base64
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
        return f"data:{file.content_type};base64,{encoded_string}"
    return None

# --- Routes ---

@app.route('/')
def index():
    """Landing Page: Fetches projects and clients from the DB."""
    conn = mysql.get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', projects=projects, clients=clients)

@app.route('/admin')
def admin():
    """Dashboard: Shows stats, leads, subscribers, and management forms."""
    conn = mysql.get_conn()
    cur = conn.cursor()
    
    # 1. Fetch Stats
    cur.execute("SELECT COUNT(*) as count FROM contact_submissions")
    lead_count = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) as count FROM subscribers")
    sub_count = cur.fetchone()['count']
    
    # 2. Fetch Data Tables
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
    """Stores a new project with an uploaded image converted to Base64."""
    name = request.form.get('name')
    desc = request.form.get('desc')
    file = request.files.get('image')
    
    img_data = get_base64_image(file)
    
    # Fallback to a default image if no file was uploaded
    if not img_data:
        img_data = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=450"

    conn = mysql.get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (name, description, image_path) VALUES (%s, %s, %s)", 
                (name, desc, img_data))
    conn.close()
    flash("Project added successfully!")
    return redirect(url_for('admin'))

@app.route('/admin/add_client', methods=['POST'])
def add_client():
    """Stores a new client testimonial with an uploaded profile picture."""
    name = request.form.get('name')
    desc = request.form.get('desc')
    designation = request.form.get('designation')
    file = request.files.get('image')
    
    img_data = get_base64_image(file)
    
    if not img_data:
        img_data = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80"

    conn = mysql.get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name, description, designation, image_path) VALUES (%s, %s, %s, %s)", 
                (name, desc, designation, img_data))
    conn.close()
    flash("Client added successfully!")
    return redirect(url_for('admin'))

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    """Handles consultation requests from the hero section."""
    conn = mysql.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contact_submissions (name, email, phone, city) VALUES (%s, %s, %s, %s)",
        (request.form['name'], request.form['email'], request.form['phone'], request.form['city'])
    )
    conn.close()
    flash("Your request has been sent!")
    return redirect(url_for('index'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Handles newsletter email subscriptions."""
    conn = mysql.get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO subscribers (email) VALUES (%s)", (request.form['email'],))
    except:
        pass # Ignore duplicates
    conn.close()
    flash("Subscribed successfully!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)