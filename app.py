#import statements
import pandas as pd
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import text
from flask_cors import CORS
from google import genai
from google.genai import types

#Configurations
app = Flask(__name__)
CORS(app)
summary2 = ""

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@localhost/Company_DB"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

GENAI_API_KEY = "AIzaSyD1K19v3xeqjFmmx78pQ63kaX4FHEvaW6c"
client = genai.Client(api_key=GENAI_API_KEY)


#posting query to genAI API
def query_genai(user_query):

    prompt = f"""
You are an AI that converts natural language into MYSQL queries.

ONLY return the MYSQL query—no explanations, formatting, or extra text.

Database Schema:
Products Table:
Columns:
product_id (BIGINT, PRIMARY KEY, AUTO_INCREMENT)
name (VARCHAR)
price (DECIMAL)
category (VARCHAR)
supplier_id (INT, FOREIGN KEY to Suppliers)

Suppliers Table:
Columns:
supplier_id (INT, PRIMARY KEY)
name (VARCHAR)
contact_name (VARCHAR)
phone (VARCHAR)
email (VARCHAR)
location (TEXT)

Now, convert this query into MYSQL:
User Query: {user_query}

Return only the MYSQL query in a SINGLE LINE in text format not code, no extra text!
    """

    response2 = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=prompt
        ),
        contents=[user_query]
    )
    response2 = str(response2.text)
    if response2.startswith("200 -"):
        response2 = response2.replace("200 -", "").strip()

    # Remove Markdown-style SQL code blocks (```)
    response2 = response2.replace("```sql", "").replace("```", "").strip()
   
    return response2
    

#executing SQL query and fetching results    
def execute_sql(sql_query):
    """
    Executes the SQL query and converts results into a CSV string.
    """
    try:
        result = db.session.execute(text(sql_query))
        rows = [dict(row) for row in result.mappings()]
       
        result_string = "\n".join(
            [", ".join(f"{key}: {value}" for key, value in row.items()) for row in rows]
        )
        summary2 = summary_info(result_string)
        return summary2, None
    
    except Exception as e:
        return None, str(e)  # Return error message
  
    
#format & summarize the results via genAI API    
def summary_info (df):
    prompt = "Display the data properly and then summarize it"
    user_query = df
    response2 = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=prompt
        ),
        contents=[user_query]
    )
    response2 = str(response2.text)
    print(response2,flush=True)
    return response2



# Routes
@app.route("/query", methods=["POST"])
def chatbot():
    data = request.json
    user_query = data.get("query")

    # Step 1: Generate SQL Query
    sql_query = query_genai(user_query)
    if not sql_query or "ERROR" in sql_query:
        return jsonify({"error": "Failed to generate SQL query."})
   
    # Step 2: Execute SQL Query
    summary2, error = execute_sql(sql_query)
    if error:
        return jsonify({"error": error})

    summary2 = summary2.replace("\n", "<br>")

    return jsonify({
        "user_query": user_query,
        "sql_query": sql_query,
        "summary": summary2
    })


@app.route("/")
def home():
    return jsonify({"message": "Chatbot API is running."})

if __name__ == "__main__":
    app.run(debug=True)
