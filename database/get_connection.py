import psycopg2
import hashlib

def get_connection():
    try:
        conn = psycopg2.connect(
            host="localhost",
            dbname="courier_db",
            user="postgres",
            password="1386",
            port="5432"
        )
        return conn
    except psycopg2.Error:
        return None

def ensure_tables():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(256) NOT NULL,
            role VARCHAR(20) NOT NULL DEFAULT 'user'
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS couriers (
            id SERIAL PRIMARY KEY,
            fullname VARCHAR(150) NOT NULL,
            phone VARCHAR(20) NOT NULL,
            status VARCHAR(20) DEFAULT 'Свободен'
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            tracking_number VARCHAR(50) UNIQUE NOT NULL,
            sender_name VARCHAR(150) NOT NULL,
            sender_address VARCHAR(255) NOT NULL,
            sender_phone VARCHAR(20),
            receiver_name VARCHAR(150) NOT NULL,
            receiver_address VARCHAR(255) NOT NULL,
            receiver_phone VARCHAR(20),
            weight DECIMAL(10, 2) NOT NULL,
            dimensions VARCHAR(50),
            declared_value DECIMAL(10, 2),
            cost DECIMAL(10, 2),
            status VARCHAR(50) DEFAULT 'Принят',
            courier_id INTEGER REFERENCES couriers(id) ON DELETE SET NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS order_history (
            id SERIAL PRIMARY KEY,
            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            old_status VARCHAR(50),
            new_status VARCHAR(50),
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    ''')
    
    try:
        hashed = hashlib.sha256("admin".encode()).hexdigest()
        cursor.execute("SELECT id FROM users WHERE username = %s;", ("admin",))
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO users (username, password, role) VALUES (%s, %s, %s);",
                ("admin", hashed, "admin")
            )
    except Exception:
        pass
        
    conn.commit()
    cursor.close()
    conn.close()