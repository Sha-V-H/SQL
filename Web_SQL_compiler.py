import streamlit as st
import sqlite3
import pandas as pd
from typing import Optional
import os

# Ensure the 'databases' directory exists
os.makedirs('databases', exist_ok=True)

# Function to execute SQL query
def execute_query(query: str, c: sqlite3.Cursor):
    c.execute(query)
    data = c.fetchall()
    return data

# Function to fetch table data
def fetch_table_data(table_name: str, conn: sqlite3.Connection):
    return pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 10", conn)

# Main function to run Streamlit app
def main():
    st.title('SQL Playground')

    # Path to the 'databases' folder
    databases_path = 'databases'
    
    # List of available databases in the 'databases' folder
    databases = [f for f in os.listdir(databases_path) if f.endswith('.db')]

    # Database selection
    selected_db: Optional[str] = st.selectbox('Select Database', databases)

    if selected_db is None:
        st.error("No database selected")
        return

    # Connect to the selected database
    conn = sqlite3.connect(os.path.join(databases_path, selected_db))
    c = conn.cursor()

    # Show tables in the selected database
    tables = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)
    st.write('Available Tables:')
    st.write(tables)

    # Allow the user to select a table to display sample data
    if not tables.empty:
        selected_table = st.selectbox('Select Table to View Data', tables['name'].tolist())

        if selected_table:
            df = fetch_table_data(selected_table, conn)
            st.write(f'Sample Data from {selected_table}')
            data_placeholder = st.empty()  # Placeholder for table data
            data_placeholder.write(df)

    st.subheader('Execute SQL Query')
    query = st.text_area('Enter SQL Query')

    if st.button('Execute'):
        if query.strip():
            try:
                c.execute(query)
                if query.strip().upper().startswith('SELECT'):
                    result = c.fetchall()
                    if result:
                        df_result = pd.DataFrame(result, columns=[i[0] for i in c.description])
                        st.write(df_result)
                    else:
                        st.warning('No results found.')
                else:
                    conn.commit()
                    st.success('Query executed successfully.')

                    # Refresh the table data if a table is selected
                    if selected_table:
                        df = fetch_table_data(selected_table, conn)
                        data_placeholder.write(df)
            except Exception as e:
                st.error(f'Error executing query: {str(e)}')

    conn.close()

if __name__ == '__main__':
    main()

