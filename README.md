# 🫒 Olive Factory Inventory Management System

A comprehensive, web-based inventory management system designed specifically for olive oil production facilities. Built with **Python (Flask)** and **MySQL**, this application tracks raw materials, finished products, supplier relationships, sales, and logistics (container tracking).

🌐 **Live Demo:** [https://benaichamelek.alwaysdata.net/](https://benaichamelek.alwaysdata.net/)

---

## 🚀 Features

### 📦 Inventory Management
- **Product Definition:** Create and categorize products (e.g., Extra Virgin Oil, Packaging).
- **Real-time Stock Tracking:** Automatically updates stock levels based on purchases and sales.
- **Low Stock Alerts:** Dashboard highlights products that have reached their minimum stock level.

### 💰 Transactions
- **Purchase Recording:** Log incoming stock from suppliers. Supports "Unknown" suppliers for informal buys.
- **Sales Recording:** Log outgoing stock to clients. Includes client name/phone tracking and stock validation (prevents overselling).
- **Financial Overview:** Dashboard displays Revenue, Spending, and Net Profit for the last 30 days.

### 🤝 Partner Management
- **Supplier Directory:** Manage supplier contact details, tax IDs, and addresses.
- **Search & Filter:** Quickly find partners or transactions using global search bars.

### 🚛 Logistics & Containers
- **Container Tracking:** Monitor the movement of identical industrial containers.
- **Net Count Calculation:** Automatically calculates available containers by tracking "Sent" vs. "Received" movements.

### 📊 Professional Dashboard
- **AdminLTE Interface:** A clean, responsive, and mobile-friendly user interface.
- **Key Metrics:** Visual cards for Total Products, Stock Efficiency, Recent Purchases, and Sales.
- **Activity Feed:** A timeline of the most recent financial transactions.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.x, Flask
- **Database:** MySQL (Hosted on Alwaysdata)
- **Frontend:** HTML5, CSS3, JavaScript
- **UI Framework:** AdminLTE 3, Bootstrap 4, FontAwesome
- **Deployment:** Alwaysdata (WSGI)

---

## 📂 Project Structure

```text
olive_factory_inventory/
├── app.py                  # Main application logic and routes
├── requirements.txt        # Python dependencies
├── templates/              # HTML templates
│   ├── base.html           # Master layout with sidebar
│   ├── login.html          # Authentication page
│   ├── dashboard.html      # Main overview
│   ├── products.html       # Product list
│   ├── add_product.html    # Define new product
│   ├── purchases.html      # Purchase history
│   ├── add_purchase.html   # Record new purchase
│   ├── sales.html          # Sales history
│   ├── add_sale.html       # Record new sale
│   ├── suppliers.html      # Supplier directory
│   ├── add_supplier.html   # Add new supplier
│   ├── containers.html     # Container tracking
│   └── add_container_movement.html # Record container movement
└── static/                 # (Optional) Custom CSS/JS
```

---

## ⚙️ Installation & Setup

### 1. Clone the Repository
```bash
git clone https://github.com/becem69/olive-factory-inventory.git
cd olive-factory-inventory
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Database Configuration
The project uses a remote MySQL database. Ensure you have the following tables created in your MySQL instance:
- `products`
- `suppliers`
- `purchases`
- `sales`
- `container_movements`

*Note: The SQL schema is provided in the `database_schema.sql` file (if included) or can be derived from the models in `app.py`.*

### 5. Run the Application
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your browser.

**Default Login:**
- **Username:** `admin`
- **Password:** `@Ud7AdaD`

> ⚠️ **Security note:** Change this password immediately after first login.

---

## 🗄️ Database Schema Highlights

| Table | Purpose |
| :--- | :--- |
| `products` | Stores item details, current quantity, and min stock levels. |
| `suppliers` | Stores partner contact information. |
| `purchases` | Links products to suppliers with quantities and prices. |
| `sales` | Links products to clients with quantities and prices. |
| `container_movements` | Tracks 'SENT' and 'RECEIVED' movements for logistics. |

---

## 📸 Screenshots

*(You can add screenshots of your Dashboard, Product List, and Container Tracking here)*

---

## 📝 License

This project is proprietary software. All rights reserved by the developer/owner unless otherwise licensed in writing.

---

## 🤝 Support

For setup assistance, customization requests, or support, please contact the developer directly.
