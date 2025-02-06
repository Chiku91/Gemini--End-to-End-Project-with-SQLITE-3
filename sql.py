from dotenv import load_dotenv
import streamlit as st
import os
import sqlite3
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Check if the API key is correctly loaded
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    st.error("Google API Key not found in environment variables.")
    st.stop()

# Configure Google Gemini API with the key
genai.configure(api_key=google_api_key)

# Function to load Google Gemini model and get responses
def get_gemini_response(question, prompt):
    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content([prompt[0], question])
        return response.text
    except Exception as e:
        st.error(f"Error in generating content from Gemini API: {e}")
        return ""

# Function to retrieve query results from SQLite database
def read_sql_query(sql, db):
    try:
        conn = sqlite3.connect(db)
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        for row in rows:
            print(row)
        conn.commit()
        conn.close()
        return rows
    except sqlite3.Error as e:
        st.error(f"Error in executing SQL query: {e}")
        return []

# Define the prompt for the Gemini model
prompt = [
    """
    You are an expert in converting English questions to SQL queries!
    The SQL database has the name STUDENT and has the following columns: NAME, CLASS, SECTION,MARKS.
    Examples:
    - How many entries of records are present? 
    SQL command: SELECT COUNT(*) FROM STUDENT;
    - Tell me all the students studying in Data Science class?
    SQL command: SELECT * FROM STUDENT WHERE CLASS='Data Science';
    The SQL query should not have any extra symbols like backticks or the word 'SQL' in the output.
    """
]

# Streamlit app configuration
st.set_page_config(page_title="Retrieve SQL Data from Gemini")
st.header("Gemini App to Retrieve SQL Data")

# Input field for the question
question = st.text_input("Enter your question:", key="input")

# Submit button
submit = st.button("Ask the question")

# If the submit button is clicked
if submit:
    if question:
        # Generate the SQL query using Gemini API
        sql_query = get_gemini_response(question, prompt)
        if sql_query:
            # Retrieve results from SQLite database
            st.subheader("The SQL query is:")
            st.code(sql_query, language="sql")
            
            results = read_sql_query(sql_query, "student.db")
            
            if results:
                st.subheader("Results:")
                for row in results:
                    st.write(row)  # Display each row of the result
            else:
                st.write("No results found or invalid query.")
    else:
        st.warning("Please enter a question.")
