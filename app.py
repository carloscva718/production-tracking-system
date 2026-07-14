from flask import Flask, request, jsonify
import mysql.connector
from datetime import datetime
import qrcode
import os
from flask import render_template
from flask import session, redirect, url_for
from werkzeug.security import check_password_hash
from functools import wraps
from flask import send_from_directory

app = Flask(__name__)
app.secret_key = 'taladro'
def conectar_bd():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="TU_CONTRASEÑA",
        database="control_produccion"
    )

def login_requerido(f):
    @wraps(f)
    def decorada(*args, **kwargs):
        if 'id_empleado' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorada

@app.route('/seleccionar_estacion', methods=['GET', 'POST'])
@login_requerido
def seleccionar_estacion():

    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':

        session['maquina_id'] = request.form['maquina_id']

        cursor.close()
        conn.close()

        return redirect(url_for('inicio'))

    cursor.execute("""
        SELECT *
        FROM maquina
        ORDER BY nombre
    """)

    maquinas = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template(
        'seleccionar_estacion.html',
        maquinas=maquinas
    )

def rol_requerido(*roles_permitidos):
    def decorador(f):
        @wraps(f)
        def decorada(*args, **kwargs):
            if 'id_empleado' not in session:
                return redirect(url_for('login'))
            if session.get('rol') not in roles_permitidos:
                return "No tienes permiso para ver esta página", 403
            return f(*args, **kwargs)
        return decorada
    return decorador

@app.route('/')
@login_requerido
def inicio():

    if 'maquina_id' not in session:
        return redirect(url_for('seleccionar_estacion'))

    return render_template("esperar_qr.html")

@app.route('/maquinas')
def listar_maquinas():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM maquina")
    resultado = cursor.fetchall()
    cursor.close()
    conn.close()
    return str(resultado)

@app.route('/lotes/nuevo', methods=['GET', 'POST'])
@rol_requerido('admin', 'produccion')
def nuevo_lote():
    if request.method == 'POST':
        numero_lote = request.form['numero_lote']
        descripcion = request.form.get('descripcion', '')
        cantidad_piezas = request.form.get('cantidad_piezas') or None
        color = request.form.get('color', '')
        tipo_canto = request.form.get('tipo_canto', '')
        grosor = request.form.get('grosor', '')

        conn = conectar_bd()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO lote (numero_lote, descripcion, cantidad_piezas, color, tipo_canto, grosor) 
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (numero_lote, descripcion, cantidad_piezas, color, tipo_canto, grosor)
        )
        conn.commit()
        nuevo_id = cursor.lastrowid
        cursor.close()
        conn.close()

        url_destino = f"http://192.168.10.103:5000/lote/{nuevo_id}"
        qr = qrcode.make(url_destino)
        carpeta = 'qr_generados'
        os.makedirs(carpeta, exist_ok=True)
        qr.save(f"{carpeta}/lote_{nuevo_id}.png")

        return redirect(url_for('ver_qr_lote', id_lote=nuevo_id))

    return render_template('nuevo_lote.html')

@app.route('/menu_produccion')
@rol_requerido('produccion', 'admin')
def menu_produccion():
    return render_template('menu_produccion.html')

@app.route('/registro/iniciar', methods=['POST'])
def iniciar_trabajo():
    lote_id = request.form['lote_id']
    maquina_id = request.form['maquina_id']
    empleado_id = session['id_empleado']

    conn = conectar_bd()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO registro_trabajo (lote_id, maquina_id, empleado_id, hora_inicio) VALUES (%s, %s, %s, %s)",
        (lote_id, maquina_id, empleado_id, datetime.now())
    )
    conn.commit()
    nuevo_id = cursor.lastrowid
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Trabajo iniciado", "id_registro": nuevo_id})

@app.route('/registro/finalizar', methods=['POST'])
def finalizar_trabajo():
    lote_id = request.form['lote_id']

    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT id_registro FROM registro_trabajo 
        WHERE lote_id = %s AND hora_fin IS NULL
        ORDER BY hora_inicio DESC LIMIT 1
    """, (lote_id,))
    registro = cursor.fetchone()

    if not registro:
        cursor.close()
        conn.close()
        return jsonify({"error": "No hay ningún registro abierto para ese lote"}), 400

    cursor.execute(
        "UPDATE registro_trabajo SET hora_fin = %s WHERE id_registro = %s",
        (datetime.now(), registro['id_registro'])
    )
    conn.commit()
    cursor.close()
    conn.close()

    return jsonify({"mensaje": "Trabajo finalizado", "id_registro": registro['id_registro']})

@app.route('/registros')
def listar_registros():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT 
            r.id_registro,
            l.numero_lote,
            m.nombre AS maquina,
            r.empleado_id,
            r.hora_inicio,
            r.hora_fin,
            TIMESTAMPDIFF(SECOND, r.hora_inicio, r.hora_fin) AS segundos_totales
        FROM registro_trabajo r
        JOIN lote l ON r.lote_id = l.id_lote
        JOIN maquina m ON r.maquina_id = m.id_maquina
    """)
    resultado = cursor.fetchall()
    cursor.close()
    conn.close()

    # Convertimos segundos en formato horas:minutos:segundos, legible
    for fila in resultado:
        segundos = fila['segundos_totales']
        if segundos is not None:
            horas = segundos // 3600
            minutos = (segundos % 3600) // 60
            segs = segundos % 60
            fila['tiempo_empleado'] = f"{horas:02d}:{minutos:02d}:{segs:02d}"

    return jsonify(resultado)

@app.route('/lotes/<int:id_lote>/ver-qr')
@rol_requerido('admin', 'produccion')
def ver_qr_lote(id_lote):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM lote WHERE id_lote = %s", (id_lote,))
    lote = cursor.fetchone()
    cursor.close()
    conn.close()
    return render_template('ver_qr.html', lote=lote)

@app.route('/qr_generados/<filename>')
def servir_qr(filename):
    return send_from_directory('qr_generados', filename)

@app.route('/lote/<int:id_lote>')
@rol_requerido('admin', 'operario')
def ver_lote(id_lote):
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM lote WHERE id_lote = %s", (id_lote,))
    lote = cursor.fetchone()
    
    cursor.execute("SELECT * FROM maquina")
    maquinas = cursor.fetchall()
    
    cursor.close()
    conn.close()
    
    return render_template('registro.html', lote=lote, maquinas=maquinas)

@app.route('/dashboard')
@rol_requerido('admin', 'direccion')
def dashboard():
    conn = conectar_bd()
    cursor = conn.cursor(dictionary=True)

    # 1. Datos generales de cada lote
    cursor.execute("SELECT id_lote, numero_lote, descripcion FROM lote ORDER BY id_lote DESC")
    lotes = cursor.fetchall()

    # 2. Detalle de cada proceso (máquina) por lote, ya con tiempo calculado
    cursor.execute("""
        SELECT 
            r.lote_id,
            m.nombre AS maquina,
            TIMESTAMPDIFF(SECOND, r.hora_inicio, r.hora_fin) AS segundos
        FROM registro_trabajo r
        JOIN maquina m ON r.maquina_id = m.id_maquina
        WHERE r.hora_fin IS NOT NULL
        ORDER BY r.hora_inicio
    """)
    procesos = cursor.fetchall()

    cursor.close()
    conn.close()

    # 3. Agrupamos los procesos bajo cada lote correspondiente
    for lote in lotes:
        procesos_del_lote = [p for p in procesos if p['lote_id'] == lote['id_lote']]

        for p in procesos_del_lote:
            segundos = int(p['segundos'] or 0)
            horas = segundos // 3600
            minutos = (segundos % 3600) // 60
            segs = segundos % 60
            p['tiempo'] = f"{horas:02d}:{minutos:02d}:{segs:02d}"

        lote['procesos'] = procesos_del_lote
        lote['num_procesos'] = len(procesos_del_lote)

        total_segundos = sum(int(p['segundos'] or 0) for p in procesos_del_lote)
        horas = total_segundos // 3600
        minutos = (total_segundos % 3600) // 60
        segs = total_segundos % 60
        lote['tiempo_total'] = f"{horas:02d}:{minutos:02d}:{segs:02d}"

    return render_template('dashboard.html', lotes=lotes)

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        id_empleado = request.form['id_empleado']
        password = request.form['password']

        conn = conectar_bd()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT * FROM empleado WHERE id_empleado = %s",
            (id_empleado,)
        )

        empleado = cursor.fetchone()

        cursor.close()
        conn.close()

        if empleado and check_password_hash(empleado['password'], password):

            session['id_empleado'] = empleado['id_empleado']
            session['nombre'] = empleado['nombre']
            session['rol'] = empleado['rol']

            if empleado['rol'] == 'admin':
                return redirect(url_for('dashboard'))

            elif empleado['rol'] == 'direccion':
                return redirect(url_for('dashboard'))

            elif empleado['rol'] == 'produccion':
                return redirect(url_for('menu_produccion'))

            elif empleado['rol'] == 'operario':
                return redirect(url_for('seleccionar_estacion'))

        return render_template(
            'login.html',
            error="Usuario o contraseña incorrectos"
        )

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')