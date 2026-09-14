import sqlite3

conn = sqlite3.connect("instance/hermes.db")
cursor = conn.cursor()

cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
print("Tablas en la BD:")
for tabla in cursor.fetchall():
    print("   - " + tabla[0])

print()
print("Columnas de la tabla 'clients':")
cursor.execute("PRAGMA table_info(clients)")
for col in cursor.fetchall():
    print("   " + col[1] + " -> " + col[2])

cursor.execute("SELECT COUNT(*) FROM clients")
count = cursor.fetchone()[0]
print()
print("Clientes registrados: " + str(count))

conn.close()
