EstateElevate: Premium Full-Stack Real Estate Platform

EstateElevate is a robust web application developed for the Flipr Placement Task. It is designed for high-end real estate firms to showcase luxury projects, manage client testimonials, and capture consultation leads through a data-driven backend.

Key Features:

1) Premium Landing Page: A modern, mobile-responsive UI featuring "Glassmorphism" design elements and a high-conversion consultation form.

2) Centralized Admin Dashboard: A secure, sidebar-driven interface for administrators to manage site content in real-time.

3) Bonus: Intelligent Image Processing: Integrated Pillow (PIL) engine that automatically crops and resizes all uploaded images to a uniform $450\times350$ aspect ratio, ensuring UI consistency.

4) Lead & Subscriber Tracking: Automated storage and display of contact form submissions and newsletter signups.

5) Dynamic Content Injection: Uses Jinja2 to render project galleries and testimonials directly from the MySQL database.

Tech Stack:

1) Backend-Python (Flask)

2) Database-MySQL

3) Frontend- Bootstrap 5, Jinja2, CSS3 (Custom Glassmorphism)

4) Libraries-Flask-MySQLDB, Pillow (Image Processing), Werkzeug

Project Structure:

/EstateElevate
│   app.py              # Main Flask application & backend logic
│   requirements.txt    # Project dependencies
│   README.md           # Documentation
├── static/
│   ├── css/
│   │   └── style.css   # Custom premium styles
│   └── uploads/        # Auto-cropped project/client images
└── templates/
    ├── index.html      # Public landing page
    └── admin.html      # Admin dashboard & management suite

Installation & Setup:

1) Clone the Repository:
   git clone https://github.com/yourusername/EstateElevate.git
   cd EstateElevate

2) Install Dependencies:
   pip install -r requirements.txt

3) Database Configuration:

Create a MySQL database named flipr_db.

Update the MYSQL_USER and MYSQL_PASSWORD in app.py.

Import your .sql schema file or run the table creation queries.

4) Run the Application:
   python app.py

  Access the site at http://127.0.0.1:5000/

Database Schema:

The relational structure is optimized for social proof and lead conversion:

Projects: Stores name, description, and cropped image paths.

Clients: Stores testimonials, designations, and headshots.

Contact_Submissions: Captures name, email, phone, and city for leads.

Subscribers: Stores unique email entries for the newsletter.
