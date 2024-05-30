import google.generativeai as genai
import mysql.connector
import os
from dotenv import load_dotenv
import json

load_dotenv()

def connect_database():
    connector = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_DATABASE')
    )
    return connector
 
 
def get_table_names():
    connector = connect_database()
    cars_query = connector.cursor()
 
    cars_query.execute("""
SELECT TABLE_NAME, COLUMN_NAME, DATA_TYPE
FROM information_schema.columns
WHERE table_schema = DATABASE()
ORDER BY table_name, ordinal_position
""")
    tables = cars_query.fetchall()
 
    connector.close()
 
    table_data = {}
    for table in tables:
        table_data[table[0]] = table_data.get(table[0], [])
        table_data[table[0]].append({
            "name": table[1],
            "type": table[2]
        })
 
    return table_data

def build_answer_prompt(user_question, query, query_results):
 
    return f"""
    Context:
    
    Analyse the User Question, SQL query and SQL Result and generate a human friendly answer.
    
    User Question:
    
    {user_question}
    
    SQL Query:
    
    {query}
    
    SQL Result:
    
    {query_results}
    
    Deliverables:
    
    Generated human friendly answer.        
    """
    
def build_query_prompt(question):
    tables = get_table_names()
 
    table_prompt = ""
    for table in tables:
        table_prompt += f"{table} has columns: " + ', '.join([f"{column['name']} ({column['type']})" for column in tables[table]]) + "\n"
    
    table_prompt+="level column of the employee_skills table can only contain Good, Bad as level. Table names and column names are lowercase."

 
    return f"""
    Context:
    
    You are provided with a MySQL database structure consisting of one or more tables. 
    Each table includes specific columns and their data types. Your task is to analyze the provided context, understand the structure of the tables, and write an SQL query to answer a 
    specific question posed by the user. Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer.
    Please make sure to not exceed the information given in the context.
    
    Table Structure:
    
    {table_prompt}
    
    User's Question:
    
    {question}
    
    Tasks:
    
    1. Analyze the provided table structure, understand the relationships and data contained within SQL Results.
    2. Write an syntactically correct SQL query that answers the user's question.
    
    Deliverables:
    
    The syntactically correct SQL query that was generated.          
    """

def query_gemini_ai(prompt):
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    return response.text

def get_query(question): 
    prompt = build_query_prompt(question)
    query = query_gemini_ai(prompt)
    query = query.replace('```sql','')
    query = query.replace('```','')
    query = query.strip()
 
    query_safety_check(query)
 
    return query

def query_safety_check(query):
    banned_actions = ['insert', 'update', 'delete', 'alter', 'drop', 'truncate', 'create', 'replace']
 
    if any(action in query for action in banned_actions):
        raise Exception("Query is not safe")
    
def get_query_results_from_database(query):
    connector = connect_database()
    employees_query = connector.cursor()
    employees_query.execute(query)
    employees = [dict((employees_query.description[i][0], value) for i, value in enumerate(row)) for row in employees_query.fetchall()]
    connector.close()
 
    return json.dumps(employees, indent=4, default=str)
 
def generate_response(question):
    query = get_query(question)
    # print("*" * 50 + "QUERY" + "*" * 50)
    # print(query)
    # print("*" * 50 + "QUERY" + "*" * 50)
    query_output = get_query_results_from_database(query)
    # print("*" * 50 + "QUERY OUTPUT" + "*" * 50)
    # print(query_output)
    # print("*" * 50 + "QUERY OUTPUT" + "*" * 50)
    retry_query_prompt = build_answer_prompt(question, query, query_output)
    # print("*" * 50 + "RETRY QUERY PROMPT" + "*" * 50)
    # print(retry_query_prompt)
    # print("*" * 50 + "RETRY QUERY PROMPT" + "*" * 50)
    generated_query = query_gemini_ai(retry_query_prompt)
    # print("*" * 50 + "GENERATED QUERY" + "*" * 50)
    # print(generated_query)
    # print("*" * 50 + "GENERATED QUERY" + "*" * 50)
    return generated_query.strip().strip('"')