
# Import necessary modules
from flask import Flask, render_template, url_for, request, redirect
import sqlite3

# Create the Flask application
app = Flask(__name__)

# Define the database connection
conn = sqlite3.connect('stamps.db')
c = conn.cursor()

# Define the routes

# Home page
@app.route('/')
def index():
    # Get all the stamps from the database
    stamps = c.execute("SELECT * FROM stamps").fetchall()

    # Render the index page and pass the stamps data
    return render_template('index.html', stamps=stamps)

# Add a new stamp
@app.route('/add_stamp', methods=['GET', 'POST'])
def add_stamp():
    # If the request is a POST request, process the form data
    if request.method == 'POST':
        # Get the form data
        country = request.form['country']
        year = request.form['year']
        denomination = request.form['denomination']
        characteristics = request.form['characteristics']

        # Insert the new stamp into the database
        c.execute("INSERT INTO stamps (country, year, denomination, characteristics) VALUES (?, ?, ?, ?)",
                  (country, year, denomination, characteristics))
        conn.commit()

        # Redirect to the home page
        return redirect(url_for('index'))

    # If the request is a GET request, render the add_stamp page
    else:
        return render_template('add_stamp.html')

# Edit an existing stamp
@app.route('/edit_stamp/<int:stamp_id>', methods=['GET', 'POST'])
def edit_stamp(stamp_id):
    # If the request is a POST request, process the form data
    if request.method == 'POST':
        # Get the form data
        country = request.form['country']
        year = request.form['year']
        denomination = request.form['denomination']
        characteristics = request.form['characteristics']

        # Update the stamp in the database
        c.execute("UPDATE stamps SET country=?, year=?, denomination=?, characteristics=? WHERE stamp_id=?",
                  (country, year, denomination, characteristics, stamp_id))
        conn.commit()

        # Redirect to the home page
        return redirect(url_for('index'))

    # If the request is a GET request, get the stamp from the database and render the edit_stamp page
    else:
        stamp = c.execute("SELECT * FROM stamps WHERE stamp_id=?", (stamp_id,)).fetchone()
        return render_template('edit_stamp.html', stamp=stamp)

# View a stamp
@app.route('/view_stamp/<int:stamp_id>')
def view_stamp(stamp_id):
    # Get the stamp from the database
    stamp = c.execute("SELECT * FROM stamps WHERE stamp_id=?", (stamp_id,)).fetchone()

    # Render the view_stamp page and pass the stamp data
    return render_template('view_stamp.html', stamp=stamp)

# User settings
@app.route('/user_settings')
def user_settings():
    # Render the user_settings page
    return render_template('user_settings.html')

# Search for stamps
@app.route('/search_stamps')
def search_stamps():
    # Get the search criteria from the request
    country = request.args.get('country')
    year = request.args.get('year')
    denomination = request.args.get('denomination')
    characteristics = request.args.get('characteristics')

    # Build the SQL query
    query = "SELECT * FROM stamps WHERE 1=1"
    if country:
        query += " AND country LIKE ?"
    if year:
        query += " AND year LIKE ?"
    if denomination:
        query += " AND denomination LIKE ?"
    if characteristics:
        query += " AND characteristics LIKE ?"

    # Execute the query and get the matching stamps
    stamps = c.execute(query, (country, year, denomination, characteristics)).fetchall()

    # Return the stamps in a JSON format
    return json.dumps(stamps)

# Export stamps
@app.route('/export_stamps')
def export_stamps():
    # Get all the stamps from the database
    stamps = c.execute("SELECT * FROM stamps").fetchall()

    # Create a CSV file with the stamp data
    with open('stamps.csv', 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['Country', 'Year', 'Denomination', 'Characteristics'])
        for stamp in stamps:
            csvwriter.writerow([stamp[1], stamp[2], stamp[3], stamp[4]])

    # Return a success message
    return "Stamps exported successfully"

# Import stamps
@app.route('/import_stamps')
def import_stamps():
    # Get the CSV file from the request
    csvfile = request.files['csvfile']

    # Read the CSV file and insert the stamps into the database
    with open(csvfile, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header row
        for row in reader:
            country, year, denomination, characteristics = row
            c.execute("INSERT INTO stamps (country, year, denomination, characteristics) VALUES (?, ?, ?, ?)",
                      (country, year, denomination, characteristics))
    conn.commit()

    # Return a success message
    return "Stamps imported successfully"

# Main block
if __name__ == '__main__':
    app.run(debug=True)
