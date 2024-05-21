from flask import Flask
from flask import request
from pymongo import MongoClient
import logging
import os
import logging_loki 



app = Flask(__name__)


handler = logging_loki.LokiHandler(
    url="http://localhost:3001/loki/api/v1/push", 
    tags={"app": "my-app2"},
    version="1",
)

os.makedirs('.logs')
logging.basicConfig(filename='.logs/student repo.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
#logging.getLogger('werkzeug').setLevel(logging.CRITICAL)
logger = logging.getLogger("app2-logger")
logger.addHandler(handler)

client = MongoClient('mongodb://localhost:27017')
db = client['students_db']
collection = db['students']



@app.route('/set_level/<new_level>', methods=['GET'])
def set_log_level(new_level):
    logger = logging.getLogger()
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if new_level.upper() in valid_levels:       
        logger.setLevel(getattr(logging, new_level.upper()))
        return f"Log level changed to {new_level.upper()}", 200
    else:
        return f"Invalid log level: {new_level}", 400

    
@app.route('/students', methods=['GET'])
def get_all_students():
    
    try:       
        students = list(collection.find({}, {'_id': 0}))
        if(students):                    
            logging.info("Viwed student data")
            logger.info("app2 Viwed student data", extra={"tags": {"service": "my-service"}})               
            return (students), 200
        else:
            logger.info("app2 NO student data available", extra={"tags": {"service": "my-service"}})
            return f'NO student data available'
    except Exception as e:
        logger.exception("app 2 exception :",exc_info=True, extra={"tags": {"service": "my-service"}})
        logging.exception("Failed to view student:{e}")
        
        #log_counter.labels(level='ERROR').inc()
        return f'Failed to view student'

@app.route('/student/<student_id>', methods=['GET'])
def get_student(student_id):
    try:
        student = collection.find_one({"ID": student_id}, {'_id': 0})
        if student:
            logging.info("Viewed individual student data")
            logger.info("Viwed individual student data", extra={"tags": {"service": "my-service"}})
            return (student), 200
        else:
            logging.error("Student not found")
            logger.error("Student not found", extra={"tags": {"service": "my-service"}})
            return f"message: Student not found", 404
    except Exception as e:
         logging.exception("Failed to retrieve student: {e}")
         logger.exception("Exception",exc_info=True,extra={"tags": {"service": "my-service"}})
         return f"message: Failed to retrieve student", 500

@app.route('/students', methods=['POST'])
def add_or_update_student():
    try:
        data = request.get_json()
        if data:    
            student_id = data['ID']
            existing_student = collection.find_one({'ID': student_id})
            if existing_student:
                collection.update_one({'ID': student_id}, {'$set': data})
                logging.info("Student data updated successfully")
                logger.info("Student data update successfully", extra={"tags": {"service": "my-service"}})
                return f'message: Student data updated successfully', 200
            else:
                collection.insert_one(data)
                logging.info("Student data added successfully")
                logger.info("Student data added successfully", extra={"tags": {"service": "my-service"}})
                return f'message: Student data added successfully', 201
        else:
            logging.error("No data provided")
            logger.error("No data provided", extra={"tags": {"service": "my-service"}})
            return f'message: No data provided', 400
    except Exception as e:
        logging.exception("Failed to retrive data: {e}")
        logger.exception("Failed to retrive data",exc_info=True, extra={"tags": {"service": "my-service"}})
        return f'message: Failed to retrive data', 400

@app.route('/student/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        deleted_student = collection.delete_one({"ID": student_id})
        if deleted_student.deleted_count > 0:
            logging.info("Student deleted successfully")
            logger.info("Student data deleted successfully", extra={"tags": {"service": "my-service"}})
            return f"message: Student deleted successfully", 200
        logging.error("Student not found")
        logger.error("Student not found", extra={"tags": {"service": "my-service"}})
        return f"message: Student not found", 404
    except Exception as e:
        logging.exception("Failed to delete student: {e}")
        logger.exception("Failed to delete student data", extra={"tags": {"service": "my-service"}})
        return f"message:Failed to delete student"
    

if __name__ == '__main__':
    app.run(port=5001)
