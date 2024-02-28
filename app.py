from flask import Flask, render_template, request, redirect, url_for, session,flash
import mysql.connector

app = Flask(__name__)


app.secret_key = 'your_secret_key'

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'inventoryms',
}

USERS = {
    'admin': {'password': 'admin', 'role': 'admin'},
    'employer': {'password': 'employer_password', 'role': 'employer'},
    'candidate': {'password': 'candidate_password', 'role': 'candidate'},
}


# creating table if not present
with mysql.connector.connect(**DB_CONFIG) as connection:
            cursor = connection.cursor()
            create_table_query = """
                CREATE TABLE IF NOT EXISTS inventory (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    quantity INT NOT NULL,
                    description TEXT
                )
            """
            cursor.execute(create_table_query)
            
            

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Check if the user exists and the password is correct
        if username in USERS and USERS[username]['password'] == password:
            session['username'] = username
            session['role'] = USERS[username]['role']

            if USERS[username]['role'] == 'employer' or USERS[username]['role'] == 'admin':
                return redirect(url_for('add_product'))
            else:
                return redirect(url_for('show_products'))
        else:
            error = 'Invalid credentials. Please try again.'
            return render_template('login.html', error=error)

    return render_template('login.html')

@app.route('/add_product', methods=['GET', 'POST'])
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        description = request.form.get('description')

        if not name or not quantity:
            flash('Name and Quantity are required fields.', 'error')
            return redirect(url_for('add_product'))

        try:
            quantity = int(quantity)
        except ValueError:
            flash('Quantity must be a valid integer.', 'error')
            return redirect(url_for('add_product'))

        with mysql.connector.connect(**DB_CONFIG) as connection:
            cursor = connection.cursor()
            cursor.execute('INSERT INTO inventory (name, quantity, description) VALUES (%s, %s, %s)',
                           (name, quantity, description))
            connection.commit()
        flash('Product added successfully!', 'success')
        return redirect(url_for('add_product'))

    return render_template('add_product.html')

@app.route('/show_products')
def show_products():
    with mysql.connector.connect(**DB_CONFIG) as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM inventory')
        products = cursor.fetchall()
    return render_template('show_products.html', products=products)


@app.route('/update_product/<int:product_id>', methods=['GET', 'POST'])
def update_product(product_id):
    if request.method == 'POST':
        name = request.form.get('name')
        quantity = request.form.get('quantity')
        description = request.form.get('description')

        if not name or not quantity:
            flash('Name and Quantity are required fields.', 'error')
            return redirect(url_for('update_product', product_id=product_id))

        try:
            quantity = int(quantity)
        except ValueError:
            flash('Quantity must be a valid integer.', 'error')
            return redirect(url_for('update_product', product_id=product_id))

        with mysql.connector.connect(**DB_CONFIG) as connection:
            cursor = connection.cursor()
            update_query = """
                UPDATE inventory
                SET name = %s, quantity = %s, description = %s
                WHERE id = %s
            """
            cursor.execute(update_query, (name, quantity, description, product_id))
            connection.commit()
        flash('Product updated successfully!', 'success')
        return redirect(url_for('show_products'))

    # Fetch the product details to pre-fill the update form
    with mysql.connector.connect(**DB_CONFIG) as connection:
        cursor = connection.cursor(dictionary=True)
        cursor.execute('SELECT * FROM inventory WHERE id = %s', (product_id,))
        product = cursor.fetchone()

    if not product:
        flash('Product not found!', 'error')
        return redirect(url_for('show_products'))

    return render_template('update_product.html', product=product)


@app.route('/remove_product/<int:product_id>', methods=['POST'])
def remove_product(product_id):
    with mysql.connector.connect(**DB_CONFIG) as connection:
        cursor = connection.cursor()
        cursor.execute('DELETE FROM inventory WHERE id = %s', (product_id,))
        connection.commit()
    flash('Product removed successfully!', 'success')
    return redirect(url_for('show_products'))


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))





if __name__ == '__main__':
    app.run(debug=True)
