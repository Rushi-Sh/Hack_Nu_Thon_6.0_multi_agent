from fpdf import FPDF

# Create a PDF document
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", size=12)

# Add a title
pdf.set_font("Arial", style="B", size=16)
pdf.cell(200, 10, "Test Case Requirements Document", ln=True, align="C")
pdf.ln(10)

# Add sample test case requirements
test_cases = [
    "1. Login Page: The system should allow users to log in using valid credentials.",
    "2. Registration Page: Users should be able to create an account with email verification.",
    "3. Dashboard: The dashboard should display user statistics and recent activity.",
    "4. File Upload: Users must be able to upload PDF documents up to 10MB.",
    "5. API Response: API should return JSON with a response time < 500ms.",
    "6. Security: The application should enforce HTTPS and prevent SQL injection.",
]

# Write test cases to the PDF
pdf.set_font("Arial", size=12)
for case in test_cases:
    pdf.multi_cell(0, 10, case)
    pdf.ln(5)

# Save the PDF
pdf_filename = "sample_test_cases.pdf"
pdf.output(pdf_filename)

pdf_filename
