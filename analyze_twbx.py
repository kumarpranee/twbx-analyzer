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

def extract_all_elements(root):
    elements = []
    for elem in root.iter():
        element_info = {
            'tag': elem.tag,
            'attributes': elem.attrib,
            'text': elem.text.strip() if elem.text else ''
        }
        elements.append(element_info)
    return elements

def extract_datasources(root):
    datasources = []
    for datasource in root.findall('.//datasource'):
        datasources.append(datasource.attrib)
    return datasources

def extract_actions(root):
    actions = []
    for action in root.findall('.//action'):
        actions.append(action.attrib)
    return actions

def extract_worksheets(root):
    worksheets = []
    for worksheet in root.findall('.//worksheet'):
        worksheets.append(worksheet.attrib)
    return worksheets

def extract_dashboards(root):
    dashboards = []
    for dashboard in root.findall('.//dashboard'):
        dashboards.append(dashboard.attrib)
    return dashboards

def extract_windows(root):
    windows = []
    for window in root.findall('.//window'):
        windows.append(window.attrib)
    return windows

def extract_datagraph(root):
    datagraph = []
    for dg in root.findall('.//datagraph'):
        datagraph.append(dg.attrib)
    return datagraph

def extract_external(root):
    external = []
    for ext in root.findall('.//external'):
        external.append(ext.attrib)
    return external

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
        'visual_configurations': [],
        'all_elements': [],
        'datasources': [],
        'actions': [],
        'worksheets': [],
        'dashboards': [],
        'windows': [],
        'datagraph': [],
        'external': []
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
    analysis_data['all_elements'] = extract_all_elements(root)
    analysis_data['datasources'] = extract_datasources(root)
    analysis_data['actions'] = extract_actions(root)
    analysis_data['worksheets'] = extract_worksheets(root)
    analysis_data['dashboards'] = extract_dashboards(root)
    analysis_data['windows'] = extract_windows(root)
    analysis_data['datagraph'] = extract_datagraph(root)
    analysis_data['external'] = extract_external(root)

    return analysis_data