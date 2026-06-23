from flask import Flask, render_template, request, redirect, url_for, flash, session
from functools import wraps
import pymysql
from datetime import date

# === DATABASE CONFIGURATION ===
DB_CONFIG = {
    'host': 'mysql-benaichamelek.alwaysdata.net',
    'port': 3306,
    'user': 'benaichamelek',
    'password': 'XyZ@155',
    'database': 'benaichamelek_factory',
    'charset': 'utf8mb4',
    'autocommit': True
}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'olive-factory-secret-key-change-in-prod'

# Fixed Credentials
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = '@Ud7AdaD'

def get_db_connection():
    try:
        return pymysql.connect(**DB_CONFIG)
    except Exception as e:
        print(f"DB Connection Failed: {e}")
        return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            flash('Please log in first.', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_container_count():
    """Calculates total containers based on Sent vs Received history"""
    conn = get_db_connection()
    count = 0
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        COALESCE(SUM(CASE WHEN movement_type = 'RECEIVED' THEN quantity ELSE 0 END), 0) -
                        COALESCE(SUM(CASE WHEN movement_type = 'SENT' THEN quantity ELSE 0 END), 0) as net_count
                    FROM container_movements
                """)
                result = cursor.fetchone()
                count = result[0] if result else 0
        finally:
            conn.close()
    return count

# === ROUTES ===

@app.route('/login', methods=['GET', 'POST'])
def login():
    if session.get('logged_in'):
        return redirect(url_for('dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            session['username'] = username
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    stats = {'total_products': 0, 'stock_efficiency': 0, 'new_purchases': 0, 'total_sales': 0}
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT COUNT(*) as cnt FROM products")
                stats['total_products'] = cursor.fetchone()['cnt']
                
                cursor.execute("SELECT ROUND(SUM(CASE WHEN current_quantity > 0 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*), 0)) as eff FROM products")
                res = cursor.fetchone()
                stats['stock_efficiency'] = int(res['eff']) if res and res['eff'] else 0
                
                cursor.execute("SELECT COUNT(*) as cnt FROM purchases WHERE purchase_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
                stats['new_purchases'] = cursor.fetchone()['cnt']
                
                cursor.execute("SELECT COUNT(*) as cnt FROM sales WHERE sale_date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
                stats['total_sales'] = cursor.fetchone()['cnt']
        except Exception as e:
            flash(f"Dashboard Error: {e}", "danger")
        finally:
            conn.close()
    return render_template('dashboard.html', stats=stats)

@app.route('/products')
@login_required
def products():
    search_query = request.args.get('search', '')
    products_list = []
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                if search_query:
                    cursor.execute("SELECT * FROM products WHERE name LIKE %s OR category LIKE %s", (f'%{search_query}%', f'%{search_query}%'))
                else:
                    cursor.execute("SELECT * FROM products ORDER BY id DESC")
                products_list = cursor.fetchall()
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            conn.close()
    return render_template('products.html', products=products_list, search=search_query)

@app.route('/add_product', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        unit = request.form.get('unit')
        
        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT id FROM products WHERE name = %s", (name,))
                    if cursor.fetchone():
                        flash(f"Product '{name}' already exists!", "warning")
                    else:
                        cursor.execute(
                            "INSERT INTO products (name, category, unit, current_quantity, min_stock_level) VALUES (%s, %s, %s, 0, 0)",
                            (name, category, unit)
                        )
                        conn.commit()
                        flash(f"Product '{name}' defined successfully.", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error: {e}", "danger")
            finally:
                conn.close()
        return redirect(url_for('products'))
    return render_template('add_product.html')

@app.route('/add_purchase', methods=['GET', 'POST'])
@login_required
def add_purchase():
    suppliers = []
    products = []
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT id, full_name FROM suppliers ORDER BY full_name")
                suppliers = cursor.fetchall()
                cursor.execute("SELECT id, name, unit FROM products ORDER BY name")
                products = cursor.fetchall()
        finally:
            conn.close()

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        supplier_id = request.form.get('supplier_id')
        quantity = float(request.form.get('quantity'))
        price_per_unit = float(request.form.get('price_per_unit'))
        purchase_date = request.form.get('purchase_date')
        notes = request.form.get('notes')
        total_price = quantity * price_per_unit

        if supplier_id == '' or supplier_id == 'unknown':
            supplier_id = None

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO purchases (product_id, supplier_id, quantity, price_per_unit, total_price, purchase_date, notes)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (product_id, supplier_id, quantity, price_per_unit, total_price, purchase_date, notes))
                    
                    cursor.execute("""
                        UPDATE products 
                        SET current_quantity = current_quantity + %s, updated_at = NOW() 
                        WHERE id = %s
                    """, (quantity, product_id))
                    
                    conn.commit()
                    flash("Purchase recorded and inventory updated!", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error: {e}", "danger")
            finally:
                conn.close()
        return redirect(url_for('purchases'))

    return render_template('add_purchase.html', suppliers=suppliers, products=products, today=date.today().isoformat())

@app.route('/purchases')
@login_required
def purchases():
    search_query = request.args.get('search', '')
    purchases_list = []
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT p.id, p.quantity, p.price_per_unit, p.total_price, p.purchase_date, p.notes,
                           pr.name as product_name, s.full_name as supplier_name
                    FROM purchases p
                    JOIN products pr ON p.product_id = pr.id
                    LEFT JOIN suppliers s ON p.supplier_id = s.id
                """
                if search_query:
                    sql += " WHERE pr.name LIKE %s OR s.full_name LIKE %s OR p.notes LIKE %s ORDER BY p.purchase_date DESC"
                    cursor.execute(sql, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
                else:
                    sql += " ORDER BY p.purchase_date DESC"
                    cursor.execute(sql)
                purchases_list = cursor.fetchall()
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            conn.close()
    return render_template('purchases.html', purchases=purchases_list, search=search_query)

@app.route('/add_sale', methods=['GET', 'POST'])
@login_required
def add_sale():
    products = []
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                cursor.execute("SELECT id, name, unit, current_quantity FROM products WHERE current_quantity > 0 ORDER BY name")
                products = cursor.fetchall()
        finally:
            conn.close()

    if request.method == 'POST':
        product_id = request.form.get('product_id')
        client_name = request.form.get('client_name')
        client_phone = request.form.get('client_phone')
        quantity = float(request.form.get('quantity'))
        price_per_unit = float(request.form.get('price_per_unit'))
        sale_date = request.form.get('sale_date')
        notes = request.form.get('notes')
        
        total_price = quantity * price_per_unit

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT current_quantity FROM products WHERE id = %s", (product_id,))
                    result = cursor.fetchone()
                    
                    if result and float(result[0]) >= quantity:
                        cursor.execute("""
                            INSERT INTO sales (product_id, client_name, client_phone, quantity, price_per_unit, total_price, sale_date, notes)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        """, (product_id, client_name, client_phone, quantity, price_per_unit, total_price, sale_date, notes))
                        
                        cursor.execute("""
                            UPDATE products 
                            SET current_quantity = current_quantity - %s, updated_at = NOW() 
                            WHERE id = %s
                        """, (quantity, product_id))
                        
                        conn.commit()
                        flash("Sale recorded and inventory updated!", "success")
                    else:
                        flash("Error: Not enough stock available for this product.", "danger")
                        
            except Exception as e:
                conn.rollback()
                flash(f"Error: {e}", "danger")
            finally:
                conn.close()
        return redirect(url_for('sales'))

    return render_template('add_sale.html', products=products, today=date.today().isoformat())

@app.route('/sales')
@login_required
def sales():
    search_query = request.args.get('search', '')
    sales_list = []
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = """
                    SELECT s.id, s.quantity, s.price_per_unit, s.total_price, s.sale_date, s.notes,
                           s.client_name, s.client_phone, pr.name as product_name
                    FROM sales s
                    JOIN products pr ON s.product_id = pr.id
                """
                
                if search_query:
                    sql += " WHERE pr.name LIKE %s OR s.client_name LIKE %s OR s.client_phone LIKE %s OR s.notes LIKE %s ORDER BY s.sale_date DESC"
                    cursor.execute(sql, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
                else:
                    sql += " ORDER BY s.sale_date DESC"
                    cursor.execute(sql)
                
                sales_list = cursor.fetchall()
        except Exception as e:
            flash(f"Error fetching sales: {str(e)}", "danger")
        finally:
            conn.close()
    else:
        flash("Could not connect to database.", "danger")

    return render_template('sales.html', sales=sales_list, search=search_query)

@app.route('/suppliers')
@login_required
def suppliers():
    search_query = request.args.get('search', '')
    suppliers_list = []
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                if search_query:
                    sql = "SELECT * FROM suppliers WHERE full_name LIKE %s OR phone_number LIKE %s OR email LIKE %s"
                    cursor.execute(sql, (f'%{search_query}%', f'%{search_query}%', f'%{search_query}%'))
                else:
                    sql = "SELECT * FROM suppliers ORDER BY full_name ASC"
                    cursor.execute(sql)
                
                suppliers_list = cursor.fetchall()
        except Exception as e:
            flash(f"Error fetching suppliers: {str(e)}", "danger")
        finally:
            conn.close()
    else:
        flash("Could not connect to database.", "danger")

    return render_template('suppliers.html', suppliers=suppliers_list, search=search_query)

@app.route('/add_supplier', methods=['GET', 'POST'])
@login_required
def add_supplier():
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        phone_number = request.form.get('phone_number')
        email = request.form.get('email')
        address = request.form.get('address')
        tax_id = request.form.get('tax_id')

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO suppliers (full_name, phone_number, email, address, tax_id)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (full_name, phone_number, email, address, tax_id))
                    conn.commit()
                    flash(f"Supplier '{full_name}' added successfully!", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error adding supplier: {str(e)}", "danger")
            finally:
                conn.close()
        return redirect(url_for('suppliers'))

    return render_template('add_supplier.html')

@app.route('/containers')
@login_required
def containers():
    current_count = get_current_container_count()
    
    search_query = request.args.get('search', '')
    movements = []
    
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor(pymysql.cursors.DictCursor) as cursor:
                sql = "SELECT * FROM container_movements"
                if search_query:
                    sql += " WHERE notes LIKE %s OR movement_type LIKE %s"
                    cursor.execute(sql, (f'%{search_query}%', f'%{search_query}%'))
                else:
                    sql += " ORDER BY movement_date DESC, id DESC"
                    cursor.execute(sql)
                movements = cursor.fetchall()
        except Exception as e:
            flash(f"Error: {e}", "danger")
        finally:
            conn.close()
            
    return render_template('containers.html', current_count=current_count, movements=movements, search=search_query)

@app.route('/add_container_movement', methods=['GET', 'POST'])
@login_required
def add_container_movement():
    if request.method == 'POST':
        movement_type = request.form.get('movement_type')
        quantity = int(request.form.get('quantity'))
        notes = request.form.get('notes')
        movement_date = request.form.get('movement_date')

        conn = get_db_connection()
        if conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        INSERT INTO container_movements (movement_type, quantity, notes, movement_date)
                        VALUES (%s, %s, %s, %s)
                    """, (movement_type, quantity, notes, movement_date))
                    conn.commit()
                    flash(f"Recorded {quantity} containers as {movement_type}.", "success")
            except Exception as e:
                conn.rollback()
                flash(f"Error: {e}", "danger")
            finally:
                conn.close()
        return redirect(url_for('containers'))

    return render_template('add_container_movement.html', today=date.today().isoformat())

if __name__ == '__main__':
    app.run(debug=True)
