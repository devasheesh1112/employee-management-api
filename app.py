
from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)
DATABASE = "employees.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS employees (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                role TEXT NOT NULL
            )
        """)


# HOME
@app.route("/employees", methods=["GET"])
def get_employees():
    name = request.args.get("name", "").strip()
    role = request.args.get("role", "").strip()

    query = "SELECT id, name, role FROM employees WHERE 1=1"
    params = []

    if name:
        query += " AND name LIKE ?"
        params.append(f"%{name}%")

    if role:
        query += " AND role LIKE ?"
        params.append(f"%{role}%")

    query += " ORDER BY id"

    with get_db_connection() as conn:
        rows = conn.execute(query, params).fetchall()

    return jsonify([dict(row) for row in rows])


# CREATE: Add employee
@app.route("/employees", methods=["POST"])
def add_employee():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body is required"}), 400

    name = data.get("name")
    role = data.get("role")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Valid name is required"}), 400

    if not isinstance(role, str) or not role.strip():
        return jsonify({"error": "Valid role is required"}), 400

    with get_db_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO employees (name, role) VALUES (?, ?)",
            (name.strip(), role.strip())
        )
        employee_id = cursor.lastrowid

        row = conn.execute(
            "SELECT id, name, role FROM employees WHERE id = ?",
            (employee_id,)
        ).fetchone()

    return jsonify(dict(row)), 201


# UPDATE: Update employee
@app.route("/employees/<int:employee_id>", methods=["PUT"])
def update_employee(employee_id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Valid JSON body is required"}), 400

    name = data.get("name")
    role = data.get("role")

    if not isinstance(name, str) or not name.strip():
        return jsonify({"error": "Valid name is required"}), 400

    if not isinstance(role, str) or not role.strip():
        return jsonify({"error": "Valid role is required"}), 400

    with get_db_connection() as conn:
        cursor = conn.execute(
            "UPDATE employees SET name = ?, role = ? WHERE id = ?",
            (name.strip(), role.strip(), employee_id)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Employee not found"}), 404

        row = conn.execute(
            "SELECT id, name, role FROM employees WHERE id = ?",
            (employee_id,)
        ).fetchone()

    return jsonify(dict(row)), 200


# DELETE: Delete employee
@app.route("/employees/<int:employee_id>", methods=["DELETE"])
def delete_employee(employee_id):
    with get_db_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM employees WHERE id = ?",
            (employee_id,)
        )

        if cursor.rowcount == 0:
            return jsonify({"error": "Employee not found"}), 404

    return jsonify({"message": "Employee deleted successfully"}), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
