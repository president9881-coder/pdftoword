import os
from flask import Flask, request, render_template_string, send_file
from pdf2docx import Converter

app = Flask(__name__)
os.makedirs('uploads', exist_ok=True)

# This is the simple HTML code for your website's interface
HTML_PAGE = """
<!doctype html>
<html lang="en">
<head>
  <title>PDF to Word Converter</title>
  <style>
    body { font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }
    form { display: inline-block; padding: 20px; border: 1px solid #ccc; border-radius: 10px; }
  </style>
</head>
<body>
  <h1>PDF to Word Converter</h1>
  <form method="post" enctype="multipart/form-data">
    <input type="file" name="file" accept=".pdf" required>
    <br><br>
    <input type="submit" value="Convert to Word">
  </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file and file.filename.endswith('.pdf'):
            pdf_path = os.path.join('uploads', file.filename)
            docx_filename = file.filename.rsplit('.', 1)[0] + '.docx'
            docx_path = os.path.join('uploads', docx_filename)
            
            # Save the uploaded PDF
            file.save(pdf_path)
            
            # Use the artifexsoftware pdf2docx tool to convert it!
            cv = Converter(pdf_path)
            cv.convert(docx_path)
            cv.close()
            
            # Send the finished DOCX back to the user to download
            return send_file(docx_path, as_attachment=True)
            
    return render_template_string(HTML_PAGE)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
