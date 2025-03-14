from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, 'TWBX File Analysis Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, 0, 1, 'L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

    def table(self, header, data):
        self.set_font('Arial', 'B', 12)
        for col in header:
            self.cell(95, 10, col, 1)
        self.ln()
        self.set_font('Arial', '', 12)
        for row in data:
            for item in row:
                self.cell(95, 10, item, 1)
            self.ln()

def generate_pdf_report(analysis_data):
    pdf = PDF()
    pdf.add_page()

    try:
        # Adding Calculated Fields
        pdf.chapter_title('Calculated Fields')
        if analysis_data['formulas']:
            formula_data = [(f"Field {i+1}", formula) for i, formula in enumerate(analysis_data['formulas'])]
            pdf.table(['Field', 'Calculation'], formula_data)
        else:
            pdf.chapter_body('No calculated fields found.')

    except Exception as e:
        print("Error generating PDF:", e)

    pdf_path = 'report.pdf'
    pdf.output(pdf_path)
    return pdf_path