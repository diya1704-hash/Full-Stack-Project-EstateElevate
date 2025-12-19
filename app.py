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
            cursorclass=pymysql.cursors.DictCursor 
        )

mysql = MySQLWrapper()

# --- Helper Function: Convert Image to Base64 ---
def get_base64_image(file):
    """Reads user-uploaded file and converts it into a Base64 string."""
    try:
        if file and file.filename != '':
            encoded_string = base64.b64encode(file.read()).decode('utf-8')
            return f"data:{file.content_type};base64,{encoded_string}"
    except Exception as e:
        print(f"Image Error: {e}")
    return None

# --- Main Routes ---

@app.route('/')
def index():
    conn = mysql.get_conn()
    cur = conn.cursor()
    
    # Trigger the upgrade
    try:
        cur.execute("ALTER TABLE projects MODIFY image_path LONGTEXT")
        cur.execute("ALTER TABLE clients MODIFY image_path LONGTEXT")
    except:
        pass

    cur.execute("SELECT * FROM projects")
    projects = cur.fetchall() # Get data first
    
    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall() # Get data first
    
    cur.close()
    conn.close() # Close last
    return render_template('index.html', projects=projects, clients=clients)

@app.route('/admin')
def admin():
    """Admin Dashboard statistics and management."""
    conn = mysql.get_conn()
    cur = conn.cursor()
    
    cur.execute("SELECT COUNT(*) as count FROM contact_submissions")
    lead_count = cur.fetchone()['count']
    cur.execute("SELECT COUNT(*) as count FROM subscribers")
    sub_count = cur.fetchone()['count']
    
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
    try:
        name = request.form.get('project_name')
        desc = request.form.get('project_desc')
        file = request.files.get('project_image')
        
        # 1. Convert to Base64
        img_data = get_base64_image(file)
        
        if not img_data:
            img_data = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=450"

        # 2. Database Connection
        conn = mysql.get_conn()
        cur = conn.cursor()
        
        # 3. Insert
        cur.execute("INSERT INTO projects (name, description, image_path) VALUES (%s, %s, %s)", 
                    (name, desc, img_data))
        conn.close()
        
        flash("Project added successfully!")
        return redirect(url_for('admin'))
        
    except Exception as e:
        # This prints the REAL error to the Vercel logs
        print(f"CRITICAL ERROR: {str(e)}")
        return f"Database Error: {str(e)}", 500

@app.route('/admin/add_client', methods=['POST'])
def add_client():
    try:
        name = request.form.get('client_name')
        desc = request.form.get('client_desc')
        designation = request.form.get('client_designation')
        
        # 1. Capture the file
        file = request.files.get('client_image') 
        
        # 2. Convert to Base64
        img_data = get_base64_image(file)
        
        # Fallback if upload fails
        if not img_data:
            img_data = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80"

        # 3. Database operation
        conn = mysql.get_conn()
        cur = conn.cursor()
        
        cur.execute(
            "INSERT INTO clients (name, description, designation, image_path) VALUES (%s, %s, %s, %s)", 
            (name, desc, designation, img_data)
        )
        conn.close()
        
        flash("Client testimonial added successfully!")
        return redirect(url_for('admin'))

    except Exception as e:
        # This will show up in your Vercel Logs
        print(f"CLIENT UPLOAD ERROR: {str(e)}")
        return f"Database Error: {str(e)}", 500

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    conn = mysql.get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contact_submissions (name, email, phone, city) VALUES (%s, %s, %s, %s)",
        (request.form['name'], request.form['email'], request.form['phone'], request.form['city'])
    )
    conn.close()
    flash("Consultation request submitted!")
    return redirect(url_for('index'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    conn = mysql.get_conn()
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO subscribers (email) VALUES (%s)", (request.form['email'],))
    except:
        pass
    conn.close()
    flash("Subscribed!")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)