import zipfile
import os
import xml.etree.ElementTree as ET

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
        field_info = {
            'caption': field.get('caption'),
            'formula': field.find('.//calculation').get('formula') if field.find('.//calculation') is not None else None
        }
        fields.append(field_info)
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