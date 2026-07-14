from werkzeug.security import generate_password_hash
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="1234",
    database="control_produccion"
)
cursor = conn.cursor()

id_empleado = 202
nombre = "Direccion Prueba"
password_plano = "direccion123"
rol = "direccion"

password_cifrada = generate_password_hash(password_plano)

cursor.execute(
    "INSERT INTO empleado (id_empleado, nombre, password, rol) VALUES (%s, %s, %s, %s)",
    (id_empleado, nombre, password_cifrada, rol)
)
conn.commit()
cursor.close()
conn.close()

print("Usuario admin creado correctamente")