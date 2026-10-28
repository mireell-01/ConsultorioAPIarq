
from datetime import date, datetime, time, timedelta

from flask import Flask, jsonify, request
import mysql.connector

app = Flask(__name__)


# =========================
# CONEXION A LA BASE DE DATOS
# =========================

def conectar():
    return mysql.connector.connect(
        host="127.0.0.1",
        port=3306,
        user="root",
        password="",
        database="Consultorio"
    )


# =========================
# CONVERSION DE DATOS A JSON
# =========================

def convertir_valor(valor):
    if isinstance(valor, timedelta):
        total_segundos = int(valor.total_seconds())
        horas, resto = divmod(total_segundos, 3600)
        minutos, segundos = divmod(resto, 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"

    if isinstance(valor, (datetime, date, time)):
        return valor.isoformat()

    return valor


def convertir_fila(fila):
    if fila is None:
        return None

    return {
        clave: convertir_valor(valor)
        for clave, valor in fila.items()
    }


# =========================
# CONSULTAS Y MODIFICACIONES
# =========================

def consultar(sql, parametros=(), uno=False):
    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor(dictionary=True)
        cursor.execute(sql, parametros)

        if uno:
            return convertir_fila(cursor.fetchone())

        return [
            convertir_fila(fila)
            for fila in cursor.fetchall()
        ]

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def modificar(sql, parametros=()):
    conexion = None
    cursor = None

    try:
        conexion = conectar()
        cursor = conexion.cursor()
        cursor.execute(sql, parametros)
        conexion.commit()

        return cursor.lastrowid, cursor.rowcount

    except Exception:
        if conexion and conexion.is_connected():
            conexion.rollback()
        raise

    finally:
        if cursor:
            cursor.close()
        if conexion and conexion.is_connected():
            conexion.close()


def obtener_datos():
    datos = request.get_json(silent=True)
    return datos if isinstance(datos, dict) else None


def datos_completos(datos, campos):
    return (
        datos is not None
        and all(
            campo in datos
            and datos[campo] is not None
            and datos[campo] != ""
            for campo in campos
        )
    )


# =========================
# INICIO Y PRUEBA DE CONEXION
# =========================

@app.route("/", methods=["GET"])
def inicio():
    return jsonify({
        "mensaje": "Servidor ConsultorioAPI funcionando"
    })


@app.route("/probar-db", methods=["GET"])
def probar_db():
    try:
        pacientes = consultar(
            "SELECT COUNT(*) AS total FROM pacientes", uno=True
        )
        citas = consultar(
            "SELECT COUNT(*) AS total FROM citas", uno=True
        )

        return jsonify({
            "conexion": "exitosa",
            "pacientes": pacientes["total"],
            "citas": citas["total"]
        })

    except mysql.connector.Error as error:
        return jsonify({
            "conexion": "fallida",
            "error": str(error)
        }), 500


# =========================
# CRUD DE PACIENTES
# =========================

@app.route("/pacientes", methods=["GET"])
def listar_pacientes():
    return jsonify(consultar(
        "SELECT * FROM pacientes ORDER BY ID"
    ))


@app.route("/pacientes/<int:id>", methods=["GET"])
def obtener_paciente(id):
    paciente = consultar(
        "SELECT * FROM pacientes WHERE ID = %s",
        (id,),
        uno=True
    )

    if paciente is None:
        return jsonify({"error": "Paciente no encontrado"}), 404

    return jsonify(paciente)


@app.route("/pacientes", methods=["POST"])
def crear_paciente():
    datos = obtener_datos()
    campos = [
        "DNI", "NOMBRE", "APELLIDO",
        "FECHA_DE_NACIMIENTO", "CELULAR"
    ]

    if not datos_completos(datos, campos):
        return jsonify({
            "error": "Envía DNI, NOMBRE, APELLIDO, "
                     "FECHA_DE_NACIMIENTO y CELULAR"
        }), 400

    try:
        nuevo_id, _ = modificar(
            """INSERT INTO pacientes
            (DNI, NOMBRE, APELLIDO, FECHA_DE_NACIMIENTO, CELULAR)
            VALUES (%s, %s, %s, %s, %s)""",
            tuple(datos[campo] for campo in campos)
        )

        return jsonify({
            "mensaje": "Paciente registrado correctamente",
            "ID": nuevo_id
        }), 201

    except mysql.connector.IntegrityError:
        return jsonify({
            "error": "El DNI ya existe o se incumplió una restricción"
        }), 409

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 400


@app.route("/pacientes/<int:id>", methods=["PUT"])
def actualizar_paciente(id):
    datos = obtener_datos()
    campos = [
        "DNI", "NOMBRE", "APELLIDO",
        "FECHA_DE_NACIMIENTO", "CELULAR"
    ]

    if not datos_completos(datos, campos):
        return jsonify({
            "error": "Envía todos los campos del paciente"
        }), 400

    try:
        _, filas = modificar(
            """UPDATE pacientes
            SET DNI=%s, NOMBRE=%s, APELLIDO=%s,
                FECHA_DE_NACIMIENTO=%s, CELULAR=%s
            WHERE ID=%s""",
            tuple(datos[campo] for campo in campos) + (id,)
        )

        if filas == 0:
            existente = consultar(
                "SELECT ID FROM pacientes WHERE ID=%s",
                (id,),
                uno=True
            )
            if existente is None:
                return jsonify({
                    "error": "Paciente no encontrado"
                }), 404

        return jsonify({"mensaje": "Paciente actualizado correctamente"})

    except mysql.connector.IntegrityError:
        return jsonify({"error": "El DNI ya existe"}), 409

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 400


@app.route("/pacientes/<int:id>", methods=["DELETE"])
def eliminar_paciente(id):
    try:
        _, filas = modificar(
            "DELETE FROM pacientes WHERE ID=%s",
            (id,)
        )

        if filas == 0:
            return jsonify({"error": "Paciente no encontrado"}), 404

        return jsonify({"mensaje": "Paciente eliminado correctamente"})

    except mysql.connector.Error:
        return jsonify({
            "error": "No se puede eliminar el paciente. "
                     "Comprueba si tiene citas asociadas."
        }), 409


# =========================
# CRUD DE CITAS
# =========================

@app.route("/citas", methods=["GET"])
def listar_citas():
    return jsonify(consultar(
        """SELECT c.ID, c.ID_PACIENTE, p.NOMBRE, p.APELLIDO,
                  c.FECHA, c.HORA, c.PRE_DIAGNOSTICO, c.ESTADO
           FROM citas c
           JOIN pacientes p ON c.ID_PACIENTE = p.ID
           ORDER BY c.ID"""
    ))


@app.route("/citas/<int:id>", methods=["GET"])
def obtener_cita(id):
    cita = consultar(
        """SELECT c.ID, c.ID_PACIENTE, p.NOMBRE, p.APELLIDO,
                  c.FECHA, c.HORA, c.PRE_DIAGNOSTICO, c.ESTADO
           FROM citas c
           JOIN pacientes p ON c.ID_PACIENTE = p.ID
           WHERE c.ID = %s""",
        (id,),
        uno=True
    )

    if cita is None:
        return jsonify({"error": "Cita no encontrada"}), 404

    return jsonify(cita)


@app.route("/citas", methods=["POST"])
def crear_cita():
    datos = obtener_datos()
    campos = [
        "ID_PACIENTE", "FECHA", "HORA",
        "PRE_DIAGNOSTICO", "ESTADO"
    ]

    if not datos_completos(datos, campos):
        return jsonify({
            "error": "Envía ID_PACIENTE, FECHA, HORA, "
                     "PRE_DIAGNOSTICO y ESTADO"
        }), 400

    if datos["ESTADO"] not in ("en espera", "atendido"):
        return jsonify({
            "error": "ESTADO debe ser 'en espera' o 'atendido'"
        }), 400

    try:
        nuevo_id, _ = modificar(
            """INSERT INTO citas
            (ID_PACIENTE, FECHA, HORA, PRE_DIAGNOSTICO, ESTADO)
            VALUES (%s, %s, %s, %s, %s)""",
            tuple(datos[campo] for campo in campos)
        )

        return jsonify({
            "mensaje": "Cita registrada correctamente",
            "ID": nuevo_id
        }), 201

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 400


@app.route("/citas/<int:id>", methods=["PUT"])
def actualizar_cita(id):
    datos = obtener_datos()
    campos = [
        "ID_PACIENTE", "FECHA", "HORA",
        "PRE_DIAGNOSTICO", "ESTADO"
    ]

    if not datos_completos(datos, campos):
        return jsonify({
            "error": "Envía todos los campos de la cita"
        }), 400

    if datos["ESTADO"] not in ("en espera", "atendido"):
        return jsonify({
            "error": "ESTADO debe ser 'en espera' o 'atendido'"
        }), 400

    try:
        _, filas = modificar(
            """UPDATE citas
            SET ID_PACIENTE=%s, FECHA=%s, HORA=%s,
                PRE_DIAGNOSTICO=%s, ESTADO=%s
            WHERE ID=%s""",
            tuple(datos[campo] for campo in campos) + (id,)
        )

        if filas == 0:
            existente = consultar(
                "SELECT ID FROM citas WHERE ID=%s",
                (id,),
                uno=True
            )
            if existente is None:
                return jsonify({"error": "Cita no encontrada"}), 404

        return jsonify({"mensaje": "Cita actualizada correctamente"})

    except mysql.connector.Error as error:
        return jsonify({"error": str(error)}), 400


@app.route("/citas/<int:id>", methods=["DELETE"])
def eliminar_cita(id):
    _, filas = modificar(
        "DELETE FROM citas WHERE ID=%s",
        (id,)
    )

    if filas == 0:
        return jsonify({"error": "Cita no encontrada"}), 404

    return jsonify({"mensaje": "Cita eliminada correctamente"})


# =========================
# EJECUCION DEL SERVIDOR
# =========================

if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )
