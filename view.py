import sqlite3
import os

DB_PATH = 'your_path_to_database.db'


if __name__ == '__main__':
    if not os.path.exists(DB_PATH):
        print('x База данных не существует!')
    else:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM deleted_messages')
        count = cursor.fetchone()[0]
        print(f'\n Всего записей: {count}')
        
        if count>0:
            cursor.execute('SELECT * FROM deleted_messages ORDER BY id DESC LIMIT 5')
            records = cursor.fetchall()
            print('\n Удаленные соообщения')
            for record in records:
                print(f' ID: {record[0]}')
                print(f"  Chat: {record[2]} (ID: {record[1]})")
                print(f"  Sender: {record[5]} {record[6]} (@{record[4]})")
                print(f"  Message: {record[8]}")
                print(f"  Deleted: {record[9]}")
                print("  " + "-" * 40)
        else:
            print("📭 В базе данных нет записей")
        input("\nНажмите Enter для выхода...")
        conn.close()

