from pydantic import BaseModel
import psycopg2
from fastapi import FastAPI, HTTPException
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Allows all
    allow_credentials=False,           # Allows cookies/headers to be sent
    allow_methods=["*"],              # Allows all standard HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],              # Allows all HTTP headers
)
connection = psycopg2.connect(
    host = os.getenv("DB_HOST"),
    port = os.getenv("DB_PORT"),
    database = os.getenv("DB_DATABASE"),
    user = os.getenv("DB_USER"),
    password = os.getenv("DB_PASSWORD")
)

cursor = connection.cursor()

class Student(BaseModel):
    id: int = None
    name: str = None
    course: str = None

#get all students
@app.get('/students')
def get_all_students():
    cursor.execute('SELECT * FROM students')
    rows = cursor.fetchall()
    print(rows)
    result = []
    for row in rows:
        result.append({
            'id' : row[0],
            'name' : row[1],
            'course' : row[2]
        })
    return result

@app.get('/students/{id}')
def get_single_student(id: int):
    try:
        cursor.execute('SELECT * FROM students WHERE id=%s', (id,))
        row = cursor.fetchone()
        return{
            'id' : row[0],
            'name' : row[1],
            'course' : row[2]
        }
    except:
        raise HTTPException(status_code=404, detail='invalid Student ID')

#Create Student record
@app.post('/students')
def create_student_record(student: Student):
    try:
        cursor.execute('insert into students values(%s, %s, %s)',(student.id, student.name, student.course))
        connection.commit()
        raise HTTPException(status_code=201, detail='Student Record Created Successfully...!')
    except psycopg2.IntegrityError:
        connection.rollback()
        raise HTTPException(status_code=404, detail='student id already exis!')


# Update Student Record        
@app.put('/students/{id}')
def update_student_record(id:int, student: Student):
    cursor.execute('UPDATE students SET id=%s, name=%s, course=%s WHERE id=%s',(student.id, student.name, student.course, id))
    if(cursor.rowcount==0):
      raise HTTPException(status_code=404, detail='Invalid ID')    
    connection.commit()
    raise HTTPException(status_code=200, detail='Student Record Created Successfully...!')

# Partial Update
@app.patch('/students/{id}')
def partial_update(id: int, student:Student):
    if(student.id != None):
        cursor.execute('UPDATE students SET id=%s WHERE id=%s' , (student.id, id))
    
    if(student.name != None):
        cursor.execute('UPDATE students SET name=%s WHERE id=%s' , (student.name, id))
    
    if(student.course != None):
        cursor.execute('UPDATE students SET course=%s WHERE id=%s' , (student.course, id))
    if(cursor.rowcount==0):
        raise HTTPException(status_code=404, detail='Invalid ID')    
    connection.commit()
    raise HTTPException(status_code=200, detail='Partial Update Successfully...!')

# Delete Student Record        
@app.delete('/students/{id}')
def delete_student_record(id: int):
    cursor.execute('DELETE FROM students WHERE id=%s', (id,) )

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail='Invalid ID')

    connection.commit()
    raise HTTPException(status_code=200,detail='Student Record deleted Successfully...!' )