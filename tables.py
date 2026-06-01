from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
import sqlite3
def connectDB():
    conn = sqlite3.connect('app.db')
    if conn:
        return conn
    else:
        return -1
tables_bp = Blueprint('tables', __name__)

@tables_bp.route('/setu/tables')

def show_tables():
    if session.get('userrole') != "Admin":
        return redirect("/")
    conn = connectDB()
    cur = conn.cursor()
    
    # Get all table names
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    table_names = [row[0] for row in cur.fetchall()]
    
    # Get data from each table
    tables_data = {}
    for table_name in table_names:
        cur.execute(f"SELECT * FROM {table_name}")
        columns = [description[0] for description in cur.description]
        rows = cur.fetchall()
        tables_data[table_name] = {
            'columns': columns,
            'rows': rows
        }
    
    conn.close()
    
    return render_template('tables.html', tables_data=tables_data)

@tables_bp.route('/setu/execute_sql', methods=['POST'])
def execute_sql():
    if session.get('userrole')!= "Admin":
        return jsonify({"Message":"Access Denied!"}),403
    sql_query = request.json.get('query', '').strip()
    
    if not sql_query:
        return jsonify({'error': 'No query provided'})
    
    conn = connectDB()
    cur = conn.cursor()
    
    try:
        cur.execute(sql_query)
        
        # Check if it's a SELECT query
        if sql_query.upper().startswith('SELECT'):
            columns = [description[0] for description in cur.description] if cur.description else []
            rows = cur.fetchall()
            conn.close()
            return jsonify({
                'success': True,
                'columns': columns,
                'rows': rows,
                'row_count': len(rows)
            })
        else:
            # For INSERT, UPDATE, DELETE, etc.
            conn.commit()
            affected = cur.rowcount
            conn.close()
            return jsonify({
                'success': True,
                'message': f'Query executed successfully. {affected} row(s) affected.',
                'affected_rows': affected
            })
    except Exception as e:
        conn.close()
        return jsonify({
            'success': False,
            'error': str(e)
        })
