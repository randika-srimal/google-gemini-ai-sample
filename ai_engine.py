import google.generativeai as genai
import mysql.connector
import os
from dotenv import load_dotenv

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

def build_prompt(question, query=None, query_output=None, chat_messages=None):
    tables = get_table_names()
 
    table_prompt = ""
    for table in tables:
        table_prompt += f"{table} has columns: " + ', '.join([f"{column['name']} ({column['type']})" for column in tables[table]]) + "\n"
 
    history = ""
    
    if chat_messages and chat_messages != "":
        history = "\n" + chat_messages
 
    query_prompt = ""
 
    if query:
        query_prompt += "SQLQuery: " + query + "\n"
        if query_output:
            query_prompt += "SQLResult: " + query_output + "\n"
        rules = "Answer: "
    else:
        rules = ("(Your answer HERE must be a syntactically correct MySQL query with no extra information or "
                 "quotes.Omit SQLQuery: from your answer)")
 
    return f"""
    You are a Human Resource Manager in a Software Company. Information about all the employees working are provided in the Context section of the question. Your main job is to help a manager to find matching employees that would fit his needs. You should ask for more information about what type of work the manager wants, but you should not exceed the information given in the context.
 
    Given an input question, first create a syntactically correct MySQL query to run, then look at the results of the query and return the answer.
    Use the following format:
    
    ---
    
    Guidelines
    
    Question: "User question here"
    SQLQuery: "SQL Query used to generate the result (if applicable)"
    SQLResult: "Result of the SQLQuery (if applicable)"
    Answer: "Final answer here (You fill this in with the SQL query only)"
    
    ---
    
    Context
    
    Only use the following tables and columns:
    
    {table_prompt}
    {history}
    
    Question: "{question}"
    {query_prompt}
    
    ---
    
    {rules}
    """

def query_gemini_ai(prompt):
    genai.configure(api_key=os.getenv('GOOGLE_GEMINI_API_KEY'))
    
    model = genai.GenerativeModel('gemini-pro')
    response = model.generate_content(prompt)

    return response.text

def get_query(question): 
    prompt = build_prompt(question)
    query = query_gemini_ai(prompt)
    query = query.strip()
 
    query_safety_check(query)
 
    return query

def query_safety_check(query):
    banned_actions = ['insert', 'update', 'delete', 'alter', 'drop', 'truncate', 'create', 'replace']
 
    if any(action in query for action in banned_actions):
        raise Exception("Query is not safe")
 
def generate_response(question):
    query = get_query(question)
    print(query)
 
    return "I'm sorry, I don't know the answer to that question. Please try again."