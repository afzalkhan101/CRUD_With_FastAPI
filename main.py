from fastapi import FastAPI , HTTPException , status 
from pydantic import BaseModel 
import mysql.connector 
import hashlib 

mydb = mysql.connector.connect(
    host = "localhost" , 
    user = "root" , 
    password = "552211", 
    database = "mydatabase" 
)

cursor = mydb.cursor()
app = FastAPI()

class DBModel(BaseModel):
    username:str 
    email:str 
    password:str 

@app.get("/users",status_code=status.HTTP_302_FOUND)
def select_users():
    select_query = "select * from users"
    cursor.execute(select_query)
    results = cursor.fetchall()
    return results 


@app.post("/users", status_code=status.HTTP_201_CREATED)
def insert_user(user: DBModel):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    insert_query = """
    INSERT INTO users (username, password, email)
    VALUES (%s, %s, %s)
    """
    values = (user.username, hashed_password, user.email)
    try:
        cursor.execute(insert_query, values)
        mydb.commit()
    except mysql.connector.Error as err:
        raise HTTPException(status_code=400, detail=f"Error: {err}")

    return {"message": "User inserted successfully"}



@app.put("/users/{user_id}", status_code=status.HTTP_200_OK)

def update_user(user_id: int, user: DBModel):
    hashed_password = hashlib.sha256(user.password.encode()).hexdigest()
    update_query = """
    UPDATE users
    SET username = %s, password = %s, email = %s
    WHERE id = %s
    """
    values = (user.username, hashed_password, user.email, user_id)

    cursor.execute(update_query, values)
    mydb.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User updated successfully"}


@app.delete("/users/{user_id}", status_code=status.HTTP_200_OK)

def delete_user(user_id: int):
    delete_query = "DELETE FROM users WHERE id = %s"
    cursor.execute(delete_query, (user_id,))
    mydb.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}