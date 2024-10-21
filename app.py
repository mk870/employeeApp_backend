import os
from flask import Flask, jsonify, make_response, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app)
url = os.environ.get("DATABASE_URL")
app.config['SQLALCHEMY_DATABASE_URI'] = url
db = SQLAlchemy(app)

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80), nullable=False)
    lastname = db.Column(db.String(80), nullable=False)
    jobtitle = db.Column(db.String(80), nullable=False)
    department = db.Column(db.String(80), nullable=False)

    def json(self):
        return {
          'id': self.id,
          'firstname': self.firstname, 
          'lastname': self.lastname,
          'jobtitle': self.jobtitle,
          'department': self.department 
          }

db.create_all()

#create a test route
@app.route('/', methods=['GET'])
def test():
  return make_response(jsonify({'message': 'test route'}), 200)

@app.route('/employees', methods=['POST'])
@cross_origin()
def create_user():
  try:
    data = request.get_json()
    newEmployee = Employee(
      firstname=data['firstname'], 
      lastname=data['lastname'],
      jobtitle=data['jobtitle'],
      department=data['department']
     )
    db.session.add(newEmployee)
    db.session.commit()
    return make_response(jsonify({'message': 'employee created'}), 201)
  except :
    return make_response(jsonify({'message': 'error creating employee'}), 500)


# get all employees
@app.route('/employees', methods=['GET'])
@cross_origin()
def get_users():
  try:
    employees = Employee.query.all()
    return make_response(jsonify([employee.json() for employee in employees]), 200)
  except:
    return make_response(jsonify({'message': 'error getting employees'}), 500)


# get an employee by id
@app.route('/employees/<int:id>', methods=['GET'])
@cross_origin()
def get_employee(id):
  try:
    employee = Employee.query.filter_by(id=id).first()
    if employee:
      return make_response(jsonify({'employee': employee.json()}), 200)
    return make_response(jsonify({'message': 'employee not found'}), 404)
  except:
    return make_response(jsonify({'message': 'error getting employee'}), 500)


# update an employee by id
@app.route('/employees/<int:id>', methods=['PUT'])
@cross_origin()
def update_employee(id):
  try:
    employee = Employee.query.filter_by(id=id).first()
    if employee:
      data = request.get_json()
      employee.firstname = data['firstname']
      employee.lastname = data['lastname']
      employee.jobtitle = data['jobtitle']
      employee.department = data['department']
      db.session.commit()
      return make_response(jsonify({'message': 'employee updated'}), 200)
    return make_response(jsonify({'message': 'employee not found'}), 404)
  except:
    return make_response(jsonify({'message': 'error updating employee'}), 500)
  


# delete an employee
@app.route('/employees/<int:id>', methods=['DELETE'])
@cross_origin()
def delete_employee(id):
  try:
    employee = Employee.query.filter_by(id=id).first()
    if employee:
      db.session.delete(employee)
      db.session.commit()
      return make_response(jsonify({'message': 'employee deleted'}), 200)
    return make_response(jsonify({'message': 'employee not found'}), 404)
  except:
    return make_response(jsonify({'message': 'error deleting employee'}), 500)



# search employee
@app.route('/search', methods=['POST'])
@cross_origin()
def search_employee():
  try:
    data = request.get_json()
    searchQuery = data["query"]
    
    firstnameResults = Employee.query.filter(Employee.firstname.ilike(f'%{searchQuery}%')).all()
    lastnameResults = Employee.query.filter(Employee.lastname.ilike(f'%{searchQuery}%')).all()
    jobTitleResults = Employee.query.filter(Employee.jobtitle.ilike(f'%{searchQuery}%')).all()
    departmentResults = Employee.query.filter(Employee.department.ilike(f'%{searchQuery}%')).all()
    employees = Employee.query.all()

    allEmployeesDict = {}
    combinedSearchResults = []

    for employee in employees:
      allEmployeesDict[employee.id]= employee.id
    
    for employee in firstnameResults:
      if employee.id in allEmployeesDict:
        combinedSearchResults.append(employee)
        allEmployeesDict.pop(employee.id)

    for employee in lastnameResults:
      if employee.id in allEmployeesDict:
        combinedSearchResults.append(employee)
        allEmployeesDict.pop(employee.id)
   
    for employee in jobTitleResults:
      if employee.id in allEmployeesDict:
        combinedSearchResults.append(employee)
        allEmployeesDict.pop(employee.id)
   
    for employee in departmentResults:
      if employee.id in allEmployeesDict:
        combinedSearchResults.append(employee)
        allEmployeesDict.pop(employee.id)
   
    return make_response(jsonify([employee.json() for employee in combinedSearchResults]), 200)
  except :
    return make_response(jsonify({'message': 'error searching employee'}), 500)

if __name__ == "__main__":
 app.run(debug=True)