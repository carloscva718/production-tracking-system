from werkzeug.security import generate_password_hash
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="control_produccion"
)
cursor = conn.cursor()

id_empleado = 201
nombre = "Jefa Producción"
password_plano = "produccion123"
rol = "produccion"

password_cifrada = generate_password_hash(password_plano)

cursor.execute(
    "INSERT INTO empleado (id_empleado, nombre, password, rol) VALUES (%s, %s, %s, %s)",
    (id_empleado, nombre, password_cifrada, rol)
)
conn.commit()
cursor.close()
conn.close()

print("Usuario de producción creado correctamente")