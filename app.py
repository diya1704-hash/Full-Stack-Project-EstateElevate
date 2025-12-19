import os
import pymysql
import base64
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'flipr_ultra_secret'

# --- Database Configuration ---
# Information retrieved from your Aiven Console connection details
MYSQL_HOST = 'mysql-608471f-diyaramawat17-b50b.k.aivencloud.com'
MYSQL_USER = 'avnadmin'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'AVNS_T820t72lxjaujRHWlrc')
MYSQL_DB = 'defaultdb'
MYSQL_PORT = 16633

class MySQLWrapper:
    def get_conn(self):
        # Locates the SSL CA certificate required for Aiven
        basedir = os.path.abspath(os.path.dirname(__file__))
        return pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            ssl={'ca': os.path.join(basedir, "ca.pem")},
            autocommit=True,
            # DictCursor allows accessing data as p['name'] instead of p[1]
            cursorclass=pymysql.cursors.DictCursor 
        )

mysql = MySQLWrapper()

# --- Helper Function: Convert Image to Base64 ---
def get_base64_image(file):
    """
    Reads the user-uploaded file and converts it into a Base64 string.
    This allows storing the image directly in the database.
    """
    if file and file.filename != '':
        # Read the binary data and encode it
        encoded_string = base64.b64encode(file.read()).decode('utf-8')
        # Return a format that HTML <img> tags can understand
        return f"data:{file.content_type};base64,{encoded_string}"
    return None

# --- Main Routes ---

@app.route('/')
def index():
    """Fetches all projects and clients to display on the landing page."""
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
    """Fetches statistics and lists for the Admin Dashboard."""
    conn = mysql.get_conn()
    cur = conn.cursor()
    
    # Get Stats for the top dashboard boxes
    cur.execute("SELECT COUNT(*) as count FROM contact_submissions")
    lead_count = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) as count FROM subscribers")
    sub_count = cur.fetchone()['count']
    
    # Get Lists of existing data
    cur.execute("SELECT * FROM contact_submissions ORDER BY submitted_at DESC")
    leads = cur.fetchall()
    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall()
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()
    
    cur.close()
    conn.close()
    return render_template('admin.html', 
                           leads=leads, 
                           projects=projects, 
                           clients=clients, 
                           lead_count=lead_count, 
                           sub_count=sub_count)

# --- Action Routes ---

@app.route('/admin/add_project', methods=['POST'])
def add_project():
    """Captures user input and image to create a new project."""
    name = request.form.get('project_name')
    desc = request.form.get('project_desc')
    # Match this key with name="project_image" in admin.html
    file = request.files.get('project_image')
    
    img_data = get_base64_image(file)
    
    # Fallback default image if the user didn't upload one
    if not img_data:
        img_data = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=450"

    conn = mysql.get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (name, description, image_path) VALUES (%s, %s, %s)", 
                (name, desc, img_data))
    cur.close()
    conn.close()
    flash("Project added successfully!")
    return redirect(url_for('admin'))

@app.route('/admin/add_client', methods=['POST'])
def add_client():
    """Captures user input and image to create a new client testimonial."""
    name = request.form.get('client_name')
    desc = request.form.get('client_desc')
    designation = request.form.get('client_designation')
    # Match this key with name="client_image" in admin.html
    file = request.files.get('client_image')
    
    img_data = get_base64_image(file)
    
    if not img_data:
        img_data = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80"

    conn = mysql.get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name, description, designation, image_path) VALUES (%s, %s, %s, %s)", 
                (name, desc, designation, img_data))
    cur.close()
    conn.close()
    flash("Client added successfully!")
    return redirect(url_for('admin'))

# --- Form Submission Routes ---

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    """Saves inquiries from the index.html consultation form."""
    conn = mysql.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contact_submissions (name, email, phone, city) VALUES (%s, %s, %s, %s)",
        (request.form['name'], request.form['email'], request.form['phone'], request.form['city'])
    )
    cur.close()
    conn.close()
    flash("Consultation request submitted!")
    return redirect(url_for('index'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    """Saves email for newsletter subscriptions."""
    conn = mysql.get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO subscribers (email) VALUES (%s)", (request.form['email'],))
    except:
        pass # Ignore duplicate emails
    cur.close()
    conn.close()
    flash("Subscribed!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)