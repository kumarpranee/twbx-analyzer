from flask import Flask, request, send_file, render_template
import os
import pandas as pd
import zipfile
from tableauhyperapi import HyperProcess, Connection, Telemetry, TableName, Name
import xml.etree.ElementTree as ET
from fpdf import FPDF

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return 'No file part', 400
    file = request.files['file']
    if file.filename == '':
        return 'No selected file', 400
    if file and file.filename.endswith('.twbx'):
        filepath = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filepath)
        try:
            excel_filepath, pdf_filepath = extract_and_convert_to_files(filepath)
            return {'message': 'File uploaded successfully', 'excel_path': excel_filepath, 'pdf_path': pdf_filepath}
        except FileNotFoundError as e:
            return str(e), 400
    return 'Invalid file format', 400

@app.route('/download', methods=['GET'])
def download_file():
    file_type = request.args.get('type')
    if file_type == 'excel':
        excel_filepath = os.path.join(DOWNLOAD_FOLDER, 'output.xlsx')
        if os.path.exists(excel_filepath):
            return send_file(excel_filepath, as_attachment=True)
        return 'Excel file not found', 404
    elif file_type == 'pdf':
        pdf_filepath = os.path.join(DOWNLOAD_FOLDER, 'output.pdf')
        if os.path.exists(pdf_filepath):
            return send_file(pdf_filepath, as_attachment=True)
        return 'PDF file not found', 404
    return 'Invalid file type', 400

def extract_and_convert_to_files(filepath):
    with zipfile.ZipFile(filepath, 'r') as z:
        z.extractall(UPLOAD_FOLDER)
        # Log the names of the extracted files
        extracted_files = z.namelist()
        print("Files extracted:", extracted_files)

        # Find the .hyper file and .twb file
        hyper_file = None
        twb_file = None
        for file in extracted_files:
            if file.endswith('.hyper'):
                hyper_file = os.path.join(UPLOAD_FOLDER, file)
            elif file.endswith('.twb'):
                twb_file = os.path.join(UPLOAD_FOLDER, file)

        if hyper_file and twb_file:
            excel_filepath = parse_hyper_and_twb_to_excel(hyper_file, twb_file)
            pdf_filepath = generate_pdf_report(twb_file)
            return excel_filepath, pdf_filepath
        else:
            raise FileNotFoundError(f'.hyper or .twb file not found. Available files: {extracted_files}')

def parse_zone(zone, dashboard_name):
    zone_style = zone.find('.//zone-style')
    border_color = zone_style.find(".//format[@attr='border-color']").get('value') if zone_style is not None and zone_style.find(".//format[@attr='border-color']") is not None else 'N/A'
    border_style = zone_style.find(".//format[@attr='border-style']").get('value') if zone_style is not None and zone_style.find(".//format[@attr='border-style']") is not None else 'N/A'
    border_width = zone_style.find(".//format[@attr='border-width']").get('value') if zone_style is not None and zone_style.find(".//format[@attr='border-width']") is not None else 'N/A'
    margin = zone_style.find(".//format[@attr='margin']").get('value') if zone_style is not None and zone_style.find(".//format[@attr='margin']") is not None else 'N/A'

    zone_detail = {
        'ID': zone.get('id'),
        'DashboardName': dashboard_name,
        'ZoneName': zone.get('name'),
        'H': zone.get('h'),
        'W': zone.get('w'),
        'X': zone.get('x'),
        'Y': zone.get('y'),
        'TypeV2': zone.get('type-v2'),
        'Param': zone.get('param'),
        'IsScaled': zone.get('is-scaled'),
        'ShowTitle': zone.get('show-title'),
        'BorderColor': border_color,
        'BorderStyle': border_style,
        'BorderWidth': border_width,
        'Margin': margin
    }
    return zone_detail

def parse_hyper_and_twb_to_excel(hyper_file, twb_file):
    output_excel = os.path.join(DOWNLOAD_FOLDER, 'output.xlsx')

    with HyperProcess(telemetry=Telemetry.SEND_USAGE_DATA_TO_TABLEAU) as hyper:
        with Connection(endpoint=hyper.endpoint, database=hyper_file) as connection:
            tables = connection.catalog.get_table_names("Extract")
            if not tables:
                raise FileNotFoundError('No tables found in the .hyper file')

            # Parse the .twb file to extract fields, calculated columns, parameters, data source details, dashboards, zones, and windows
            tree = ET.parse(twb_file)
            root = tree.getroot()

            fields_data = []
            calculated_fields_data = []
            parameters_data = []
            datasources_data = []
            dashboards_data = []
            zones_data = []
            windows_data = []

            for datasource in root.findall('.//datasource'):
                if datasource.get('hasconnection', 'true') == 'false':
                    continue  # Exclude data sources with hasconnection='false'
                if 'Parameters' in datasource.get('name', ''):
                    continue  # Exclude data sources with name containing 'Parameters'

                datasource_detail = {
                    'Name': datasource.get('name'),
                    'Caption': datasource.get('caption', '')
                }
                
                named_connection = datasource.find(".//connection/named-connections/named-connection/connection")
                if named_connection is not None:
                    datasource_detail.update({
                        'Class': named_connection.get('class', 'N/A'),
                        'Cleaning': named_connection.get('cleaning', 'N/A'),
                        'Compat': named_connection.get('compat', 'N/A'),
                        'DataRefreshTime': named_connection.get('dataRefreshTime', 'N/A'),
                        'InterpretationMode': named_connection.get('interpretationMode', 'N/A'),
                        'Validate': named_connection.get('validate', 'N/A'),
                        'WorkgroupAuthMode': named_connection.get('workgroup-auth-mode', 'N/A')
                    })
                
                datasources_data.append(datasource_detail)

                for column in datasource.findall('.//column'):
                    if '[__tableau_internal_object_id__]' in column.get('name', ''):
                        continue  # Exclude columns with name like [__tableau_internal_object_id__]

                    field = {
                        'Name': column.get('name'),
                        'Hidden': column.get('hidden', 'false'),
                        'Type': column.get('datatype'),
                        'Role': column.get('role'),
                        'Calculation': '',
                        'Datasource Name': datasource.get('name')
                    }
                    calculation = column.find('.//calculation')
                    if calculation is not None:
                        field['Calculation'] = calculation.get('formula')
                        field['Caption'] = column.get('caption', '')
                        calculated_fields_data.append(field)
                    else:
                        fields_data.append(field)

            for parameter in root.findall('.//parameter'):
                param = {
                    'Name': parameter.get('name'),
                    'Caption': parameter.get('caption', ''),
                    'Datatype': parameter.get('datatype'),
                    'CurrentValue': parameter.get('currentValue')
                }
                parameters_data.append(param)

            for dashboard in root.findall('.//dashboards/dashboard'):
                size = dashboard.find('.//size')
                dashboard_detail = {
                    'DashboardName': dashboard.get('name'),
                    'MaxWidth': size.get('maxwidth') if size is not None else 'N/A',
                    'MaxHeight': size.get('maxheight') if size is not None else 'N/A',
                    'MinWidth': size.get('minwidth') if size is not None else 'N/A',
                    'MinHeight': size.get('minheight') if size is not None else 'N/A',
                    'SizingMode': size.get('sizing-mode') if size is not None else 'N/A'
                }
                dashboards_data.append(dashboard_detail)

                zones = dashboard.findall('.//zones/zone')
                for zone in zones:
                    zone_detail = parse_zone(zone, dashboard.get('name'))
                    zones_data.append(zone_detail)

                    nested_zones = zone.findall('.//zone')
                    for nested_zone in nested_zones:
                        nested_zone_detail = parse_zone(nested_zone, dashboard.get('name'))
                        zones_data.append(nested_zone_detail)

            for window in root.findall('.//windows/window'):
                window_detail = {
                    'Class': window.get('class'),
                    'Maximized': window.get('maximized'),
                    'Name': window.get('name'),
                    'TabColor': window.get('tab-color'),
                    'Hidden': window.get('hidden')
                }
                windows_data.append(window_detail)

            # Remove duplicate data and records where Role is empty
            df_fields = pd.DataFrame(fields_data).drop_duplicates()
            df_fields = df_fields[df_fields['Role'].notna() & (df_fields['Role'] != '')]
            df_calculated_fields = pd.DataFrame(calculated_fields_data).drop_duplicates()
            df_parameters = pd.DataFrame(parameters_data).drop_duplicates()
            df_datasources = pd.DataFrame(datasources_data).drop_duplicates(subset=['Name'])
            df_dashboards = pd.DataFrame(dashboards_data).drop_duplicates()
            df_zones = pd.DataFrame(zones_data).drop_duplicates()
            df_windows = pd.DataFrame(windows_data).drop_duplicates()

            with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
                df_datasources.to_excel(writer, sheet_name='DataSources', index=False)
                df_fields.to_excel(writer, sheet_name='Fields', index=False)
                df_calculated_fields.to_excel(writer, sheet_name='Calculated Fields', index=False)
                df_parameters.to_excel(writer, sheet_name='Parameters', index=False)
                df_dashboards.to_excel(writer, sheet_name='Dashboards', index=False)
                df_zones.to_excel(writer, sheet_name='Zones', index=False)
                df_windows.to_excel(writer, sheet_name='Windows', index=False)

    return output_excel

def generate_pdf_report(twb_file):
    output_pdf = os.path.join(DOWNLOAD_FOLDER, 'output.pdf')

    # Parse the .twb file to extract data source details and fields
    tree = ET.parse(twb_file)
    root = tree.getroot()

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    for datasource in root.findall('.//datasource'):
        if datasource.get('hasconnection', 'true') == 'false':
            continue  # Exclude data sources with hasconnection='false'
        if 'Parameters' in datasource.get('name', ''):
            continue  # Exclude data sources with name containing 'Parameters'

        # Add data source caption
        caption = datasource.get('caption', '')
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(200, 10, txt=f"Datasource: {caption}", ln=True, align='L')

        # Add table header
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(60, 10, txt="Name", border=1)
        pdf.cell(60, 10, txt="Type", border=1)
        pdf.cell(60, 10, txt="Role", border=1)
        pdf.ln()

        # Add fields
        pdf.set_font("Arial", size=10)
        for column in datasource.findall('.//column'):
            if '[__tableau_internal_object_id__]' in column.get('name', ''):
                continue  # Exclude columns with name like [__tableau_internal_object_id__]
            name = column.get('name', '')
            type_ = column.get('datatype', '')
            role = column.get('role', '')
            pdf.cell(60, 10, txt=name, border=1)
            pdf.cell(60, 10, txt=type_, border=1)
            pdf.cell(60, 10, txt=role, border=1)
            pdf.ln()

    pdf.output(output_pdf)
    return output_pdf

if __name__ == '__main__':
    app.run(debug=True)