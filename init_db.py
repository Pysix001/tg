import sqlite3

def init_db():
    conn = sqlite3.connect('keys.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS keys (key TEXT)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS used_keys (key TEXT)''')
    
    # Добавляем тестовые ключи (можно удалить)
    test_keys = ["KEY-111-ETH", "KEY-222-ETH", "KEY-333-ETH"]
    cursor.executemany("INSERT INTO keys (key) VALUES (?)", [(k,) for k in test_keys])
    
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()