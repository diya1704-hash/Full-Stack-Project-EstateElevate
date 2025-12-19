import os
import pymysql
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = 'flipr_ultra_secret'

# Database Configuration
MYSQL_HOST = 'mysql-608471f-diyaramawat17-b50b.k.aivencloud.com'
MYSQL_USER = 'avnadmin'
MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD', 'AVNS_T820t72lxjaujRHWlrc')
MYSQL_DB = 'defaultdb'
MYSQL_PORT = 16633

class MySQLWrapper:
    @property
    def connection(self):
        basedir = os.path.abspath(os.path.dirname(__file__))
        return pymysql.connect(
            host=MYSQL_HOST,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD,
            database=MYSQL_DB,
            port=MYSQL_PORT,
            ssl={'ca': os.path.join(basedir, "ca.pem")},
            autocommit=True
        )

mysql = MySQLWrapper()

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
    # VERCEL FIX: Instead of saving to a locked disk, we use a high-quality placeholder.
    # This allows you to submit the form without the server crashing.
    img_path = "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=450&h=350&fit=crop"
    
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("INSERT INTO projects (name, description, image_path) VALUES (%s, %s, %s)", 
                (request.form['name'], request.form['desc'], img_path))
    conn.close()
    return redirect(url_for('admin'))

@app.route('/admin/add_client', methods=['POST'])
def add_client():
    # VERCEL FIX: Using a professional avatar URL for clients
    img_path = "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=80&h=80&fit=crop"
    
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute("INSERT INTO clients (name, description, designation, image_path) VALUES (%s, %s, %s, %s)", 
                (request.form['name'], request.form['desc'], request.form['designation'], img_path))
    conn.close()
    return redirect(url_for('admin'))

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    conn = mysql.connection
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO contact_submissions (name, email, phone, city) VALUES (%s, %s, %s, %s)",
        (request.form['name'], request.form['email'], request.form['phone'], request.form['city'])
    )
    conn.close()
    flash("Request sent successfully!")
    return redirect(url_for('index'))

@app.route('/subscribe', methods=['POST'])
def subscribe():
    conn = mysql.connection
    cur = conn.cursor()
    try:
        cur.execute("INSERT INTO subscribers (email) VALUES (%s)", (request.form['email'],))
    except:
        pass
    conn.close()
    return redirect(url_for('index'))

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

app = app

if __name__ == '__main__':
    app.run(debug=True)