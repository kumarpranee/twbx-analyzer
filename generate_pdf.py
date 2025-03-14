from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'TWBX File Analysis Report', 0, 1, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(10)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def sub_chapter_title(self, title):
        self.set_font('Arial', 'B', 10)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def sub_chapter_body(self, body):
        self.set_font('Arial', '', 10)
        self.multi_cell(0, 10, body)
        self.ln()

def generate_pdf_report(analysis_data):
    pdf = PDF()
    pdf.add_page()

    # Adding Formulas
    pdf.chapter_title('Formulas')
    if analysis_data['formulas']:
        for formula in analysis_data['formulas']:
            pdf.chapter_body(formula)
    else:
        pdf.chapter_body('No formulas found.')

    # Adding Fields
    pdf.chapter_title('Fields')
    if analysis_data['fields']:
        for field in analysis_data['fields']:
            pdf.chapter_body(field)
    else:
        pdf.chapter_body('No fields found.')

    # Adding Connections
    pdf.chapter_title('Connections')
    if analysis_data['connections']:
        for connection in analysis_data['connections']:
            conn_info = f"Type: {connection['type']}, DB Name: {connection['dbname']}, Server: {connection['server']}"
            pdf.chapter_body(conn_info)
    else:
        pdf.chapter_body('No connections found.')

    # Adding Visuals
    pdf.chapter_title('Visuals')
    if analysis_data['visual_names']:
        for i, visual_name in enumerate(analysis_data['visual_names']):
            pdf.sub_chapter_title(f"Visual {i + 1}: {visual_name}")
            configurations = analysis_data['visual_configurations'][i]
            if configurations:
                for config in configurations:
                    pdf.sub_chapter_body(config)
            else:
                pdf.sub_chapter_body('No configurations found.')
    else:
        pdf.chapter_body('No visuals found.')

    pdf_path = 'report.pdf'
    pdf.output(pdf_path)
    return pdf_path