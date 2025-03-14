import zipfile
import os
import xml.etree.ElementTree as ET
import psycopg2

def extract_twb_file(file_path, extract_to='extracted'):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)
    for root, dirs, files in os.walk(extract_to):
        for file in files:
            if file.endswith('.twb'):
                return os.path.join(root, file)
    return None

def parse_twb_file(twb_file_path):
    tree = ET.parse(twb_file_path)
    root = tree.getroot()
    return root

def extract_formulas(root):
    formulas = []
    for formula in root.findall('.//calculation'):
        formulas.append(formula.get('formula'))
    return formulas

def extract_fields(root):
    fields = []
    for field in root.findall('.//column'):
        fields.append(field.get('caption'))
    return fields

def extract_connections(root):
    connections = []
    for connection in root.findall('.//connection'):
        conn_info = {
            'type': connection.get('class'),
            'dbname': connection.get('dbname'),
            'server': connection.get('server')
        }
        connections.append(conn_info)
    return connections

def extract_visuals(root):
    visuals = []
    for worksheet in root.findall('.//worksheet'):
        visual_info = {
            'name': worksheet.get('name'),
            'configurations': [config.get('name') for config in worksheet.findall('.//viz')]
        }
        visuals.append(visual_info)
    return visuals

def analyze_twbx_file(file_path):
    analysis_data = {
        'formulas': [],
        'fields': [],
        'connections': [],
        'visual_names': [],
        'visual_configurations': []
    }

    twb_file = extract_twb_file(file_path)
    if not twb_file:
        raise FileNotFoundError('No .twb file found in the provided .twbx file.')

    root = parse_twb_file(twb_file)

    analysis_data['formulas'] = extract_formulas(root)
    analysis_data['fields'] = extract_fields(root)
    analysis_data['connections'] = extract_connections(root)
    visuals = extract_visuals(root)
    analysis_data['visual_names'] = [visual['name'] for visual in visuals]
    analysis_data['visual_configurations'] = [visual['configurations'] for visual in visuals]

    return analysis_data

def load_data_to_db(analysis_data, db_config):
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()

        # Create table schema
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis_data (
                id SERIAL PRIMARY KEY,
                field TEXT,
                calculation TEXT,
                connection_type TEXT,
                connection_dbname TEXT,
                connection_server TEXT,
                visual_name TEXT,
                visual_configurations TEXT
            )
        """)
        conn.commit()

        # Insert formulas
        for formula in analysis_data['formulas']:
            cursor.execute("INSERT INTO analysis_data (field, calculation) VALUES (%s, %s)", (None, formula))

        # Insert fields
        for field in analysis_data['fields']:
            cursor.execute("INSERT INTO analysis_data (field) VALUES (%s)", (field,))

        # Insert connections
        for connection in analysis_data['connections']:
            cursor.execute("INSERT INTO analysis_data (connection_type, connection_dbname, connection_server) VALUES (%s, %s, %s)",
                            (connection['type'], connection['dbname'], connection['server']))

        # Insert visuals
        for visual_name, configurations in zip(analysis_data['visual_names'], analysis_data['visual_configurations']):
            cursor.execute("INSERT INTO analysis_data (visual_name, visual_configurations) VALUES (%s, %s)",
                            (visual_name, ', '.join(configurations)))

        conn.commit()

    except Exception as error:
        print(f"Error loading data to database: {error}")

    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    file_path = 'path_to_your_twbx_file.twbx'
    db_config = {
        'dbname': 'your_db_name',
        'user': 'your_db_user',
        'password': 'your_db_password',
        'host': 'your_db_host',
        'port': 'your_db_port'
    }

    analysis_data = analyze_twbx_file(file_path)
    load_data_to_db(analysis_data, db_config)