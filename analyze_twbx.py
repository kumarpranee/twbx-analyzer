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

def extract_dashboards_with_viewpoints(root):
    dashboards = []
    for window in root.findall(".//window[@class='dashboard']"):
        dashboard_name = window.get('name')
        viewpoints = [vp.get('name') for vp in window.findall('.//viewpoint')]
        for viewpoint in viewpoints:
            dashboard_info = {
                'name': window.get('name'),
                'visuals_to_include': viewpoint  # Each viewpoint will be a separate row
            }
            dashboards.append(dashboard_info)
    return dashboards

def analyze_twbx_file(file_path):
    analysis_data = {
        'dashboards': []
    }

    twb_file = extract_twb_file(file_path)
    if not twb_file:
        raise FileNotFoundError('No .twb file found in the provided .twbx file.')

    root = parse_twb_file(twb_file)

    analysis_data['dashboards'] = extract_dashboards_with_viewpoints(root)

    return analysis_data