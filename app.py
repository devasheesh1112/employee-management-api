
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


@app.route("/employees", methods=["GET"])
def get_employees():
    try:
        page = int(request.args.get("page", 1))
        limit = int(request.args.get("limit", 5))

        if page < 1 or limit < 1 or limit > 100:
            return jsonify({
                "error": "page must be >= 1 and limit must be between 1 and 100"
            }), 400

        offset = (page - 1) * limit

        with get_db_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, name, role
                FROM employees
                ORDER BY id
                LIMIT ? OFFSET ?
                """,
                (limit, offset)
            ).fetchall()

            total = conn.execute(
                "SELECT COUNT(*) FROM employees"
            ).fetchone()[0]

        return jsonify({
            "page": page,
            "limit": limit,
            "total": total,
            "employees": [dict(row) for row in rows]
        }), 200

    except ValueError:
        return jsonify({"error": "page and limit must be integers"}), 400


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



@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "HTTP method not allowed"}), 405


@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Internal server error"}), 500



if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
