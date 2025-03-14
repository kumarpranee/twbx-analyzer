import pandas as pd

def generate_excel_report(analysis_data, output_path='report.xlsx'):
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

    # Create DataFrame for dashboards with viewpoints and name the sheet as "Visuals Required"
    if analysis_data['dashboards']:
        dashboards_df = pd.DataFrame(analysis_data['dashboards'])
    else:
        dashboards_df = pd.DataFrame(columns=['Name', 'Viewpoint'])
    dashboards_df.to_excel(writer, sheet_name='Visuals Required', index=False)

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

    return output_path