import xml.etree.ElementTree as ET
import json
import sys

# Function to convert an XML file to a list of employee and manager pairs
def convert_xml(file_url: str) -> list:
    tree = ET.parse(file_url)
    root = tree.getroot()

    employees = []

    # Iterate through the XML structure to extract employee and manager info
    for child in root:
        employees.append([
            child.find("field[@id='email']").text,
            child.find("field[@id='manager']").text
        ])
    
    return employees

# Class to represent an individual employee with their email, manager, and direct reports
class Employee:
    def __init__(self, email, manager):
        self.email = email
        self.manager = manager
        self.direct_reports = []

# Class to handle the creation of the organizational hierarchy
class Hierarchy:
    top_managers = [] # List to store top-level managers (employees with no manager)
    employees_dict = {} # Dictionary to map employee emails to Employee objects

    # Function to process the flat employee-manager list and populate employee objects
    def getData(self, arr):
        for e in arr:
            email = e[0]
            manager = e[1]
            employee = Employee(email, manager)
            self.employees_dict[email] = employee
            if manager == None:
                self.top_managers.append(employee)
    
    # Function to retrieve all subordinates of a given manager
    def getSubordinates(self, manager):
        subordinates_arr = []
        for e in self.employees_dict.values():
            if e.manager == manager:
                subordinates_arr.append(e)
        return subordinates_arr

    # Recursive function to build the organizational tree
    def buildTree(self, top_m):
        emp = top_m
        subordinates = self.getSubordinates(top_m.email)
        emp.direct_reports = subordinates
        if len(subordinates) == 0:
            return # Base case: if no subordinates, return
        for subordinate in subordinates:
            self.buildTree(subordinate)
        
    # Recursive function to create a dictionary representation of an employee and their direct reports
    def createRootDict(self, root):
        reps = root.direct_reports

        root_dict = {
            "employee": {
                "email": root.email,
                "direct_reports": [self.createRootDict(rep) for rep in reps]
            }
        }
        return root_dict

    # Function to create a list of top-level managers with their subordinates in a tree structure    
    def createRootArr(self):
        result = []
        for top_manager in self.top_managers:
            self.buildTree(top_manager)
            result.append(self.createRootDict(top_manager))
        return result

# Function to write the resulting organizational chart to a JSON file
def create_json_file(file_name: str, result_dict: dict):
    file_path = f'{file_name}.json'
    with open(file_path, 'w') as json_file:
        json.dump(result_dict, json_file, indent = 3)

# Main block of code
if __name__ ==  '__main__':
    # Ensure the correct number of arguments is provided
    if len(sys.argv) != 2:
        print('In order to execute this script use this syntax: python/python3 <this_file.py> <input.xml>')
    else:
        employees_arr = convert_xml(sys.argv[1])

        tree = Hierarchy()
        tree.getData(employees_arr)

        result = tree.createRootArr()

        create_json_file('output', result)