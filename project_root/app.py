import json
import os
from flask import Flask, request, jsonify
import time
import uuid


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STORAGE_FILE = os.path.join(BASE_DIR, 'storage.json')
SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'screenshots')


if not os.path.exists(SCREENSHOTS_DIR):
    os.makedirs(SCREENSHOTS_DIR)


app = Flask(__name__)


# Persistence Helpers
def load_data():
    if os.path.exists(STORAGE_FILE):
        with open(STORAGE_FILE, 'r') as f:
            return json.load(f)
    else:
        return {"employees": [], "projects": [], "tasks": [], "timeLogs": [], "screenshots": []}


def save_data(data):
    with open(STORAGE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


# Helper: Generate Unique IDs
def generate_id():
    return str(uuid.uuid4())


# --- APIs ---


@app.route('/employee', methods=['POST'])
def add_employee():
    data_in = request.json
    data = load_data()
    emp = {
        "id": generate_id(),
        "name": data_in["name"],
        "email": data_in["email"],
        "active": True,
        "createdAt": int(time.time() * 1000)
    }
    data['employees'].append(emp)
    save_data(data)
    print(f"Activation link: http://localhost:5001/activate/{emp['id']}")
    return jsonify(emp)


@app.route('/employee', methods=['GET'])
def get_employees():
    data = load_data()
    return jsonify(data['employees'])


@app.route('/project', methods=['POST'])
def add_project():
    data_in = request.json
    data = load_data()
    proj = {
        "id": generate_id(),
        "name": data_in["name"],
        "employeeIds": data_in.get("employeeIds", []),
        "createdAt": int(time.time() * 1000)
    }
    data['projects'].append(proj)


    task = {
        "id": generate_id(),
        "name": f"Default Task for {proj['name']}",
        "projectId": proj['id'],
        "employeeIds": data_in.get("employeeIds", []),
        "createdAt": int(time.time() * 1000)
    }
    data['tasks'].append(task)
    save_data(data)
    return jsonify(proj)


@app.route('/project', methods=['GET'])
def get_projects():
    data = load_data()
    return jsonify(data['projects'])


@app.route('/task', methods=['GET'])
def get_tasks():
    data = load_data()
    return jsonify(data['tasks'])


@app.route('/time', methods=['POST'])
def log_time():
    data_in = request.json
    data = load_data()
    data['timeLogs'].append(data_in)
    save_data(data)
    return jsonify({"status": "Time logged successfully"})


@app.route('/time', methods=['GET'])
def get_time_logs():
    data = load_data()
    return jsonify(data['timeLogs'])


@app.route('/screenshot', methods=['POST'])
@app.route('/screenshot', methods=['POST'])
def upload_screenshot():
    data_in = request.form
    file = request.files['file']
    employeeId = data_in['employeeId']
    employeeName = data_in['employeeName'].replace(" ", "_")  # sanitize name
    projectName = data_in['projectName'].replace(" ", "_")    # sanitize name
    timestamp = data_in['timestamp']
    permission = data_in['permission']


    # Directory structure: screenshots/ProjectName/EmployeeName/
    project_dir = os.path.join(SCREENSHOTS_DIR, projectName)
    employee_dir = os.path.join(project_dir, employeeName)


    os.makedirs(employee_dir, exist_ok=True)


    filename = f"{employeeId}_{timestamp}.png"
    filepath = os.path.join(employee_dir, filename)
    try:
        file.save(filepath)
    except Exception as e:
        return jsonify({"status": "Failed", "error": str(e)}), 500


    # Update storage.json metadata
    data = load_data()
    data['screenshots'].append({
        "employeeId": employeeId,
        "employeeName": employeeName,
        "projectName": projectName,
        "timestamp": timestamp,
        "permission": permission,
        "filename": os.path.relpath(filepath, start=BASE_DIR)
    })
    save_data(data)


    return jsonify({"status": "Screenshot saved"})






@app.route('/screenshot', methods=['GET'])
def get_screenshots():
    data = load_data()
    return jsonify(data['screenshots'])


# Run Backend Server
if __name__ == "__main__":
    app.run(port=5000)






