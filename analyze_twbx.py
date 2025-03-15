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

def extract_worksheets_and_tables(root):
    worksheets = []
    for worksheet in root.findall(".//worksheet"):
        worksheet_name = worksheet.get('name')
        for table in worksheet.findall(".//table"):
            table_name = table.get('name')
            view = table.find(".//view")
            style = table.find(".//style")
            rows = table.find(".//rows")
            cols = table.find(".//cols")
            
            for panes in table.findall(".//panes"):
                for pane in panes.findall(".//pane"):
                    pane_name = pane.get('id')
                    # Removed the for loop for encodings
                    element_info = {
                        'worksheet': worksheet_name,
                        'table': table_name,
                        'view': view.get('name') if view is not None else None,
                        'style': style.get('name') if style is not None else None,
                        'pane': pane_name,
                        'rows': rows.get('name') if rows is not None else None,
                        'cols': cols.get('name') if cols is not None else None
                    }
                    worksheets.append(element_info)
    return worksheets

def analyze_twbx_file(file_path):
    analysis_data = {
        'dashboards': [],
        'worksheets': []
    }

    twb_file = extract_twb_file(file_path)
    if not twb_file:
        raise FileNotFoundError('No .twb file found in the provided .twbx file.')

    root = parse_twb_file(twb_file)

    analysis_data['dashboards'] = extract_dashboards_with_viewpoints(root)
    analysis_data['worksheets'] = extract_worksheets_and_tables(root)

    return analysis_data