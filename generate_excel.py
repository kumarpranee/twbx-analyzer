import pandas as pd

def generate_excel_report(analysis_data, output_path='report.xlsx'):
    writer = pd.ExcelWriter(output_path, engine='xlsxwriter')

    # Create DataFrame for dashboards with visuals to include and name the sheet as "Pages To Create"
    if analysis_data['dashboards']:
        dashboards_df = pd.DataFrame(analysis_data['dashboards'])
    else:
        dashboards_df = pd.DataFrame(columns=['Dashboard', 'Visuals to Include'])
    dashboards_df.to_excel(writer, sheet_name='Pages To Create', index=False)

    # Close the Pandas Excel writer and output the Excel file.
    writer.close()

    return output_path