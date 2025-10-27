from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from io import BytesIO
from pypdf import PdfReader, PdfWriter
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

MERGED_STORE = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/merge', methods=['POST'])
def merge():
    files = request.files.getlist('pdfFiles')
    if not files or len(files) < 2:
        flash('Please select at least 2 PDF files to merge.')
        return redirect(url_for('home'))

    writer = PdfWriter()
    for f in files:
        if f and f.filename:
            reader = PdfReader(f.stream)
            for page in reader.pages:
                writer.add_page(page)

    output = BytesIO()
    writer.write(output)
    writer.close()
    output.seek(0)

    token = secrets.token_urlsafe(16)
    MERGED_STORE[token] = output.read()
    return redirect(url_for('result', token=token))

@app.route('/result/<token>')
def result(token):
    if token not in MERGED_STORE:
        flash('Your merged file is no longer available. Please merge again.')
        return redirect(url_for('home'))
    return render_template('result.html', token=token)

@app.route('/download/<token>')
def download(token):
    data = MERGED_STORE.get(token)
    if not data:
        flash('Your merged file is no longer available. Please merge again.')
        return redirect(url_for('home'))

    return send_file(BytesIO(data), mimetype='application/pdf',
                     as_attachment=True, download_name='merged.pdf')

if __name__ == '__main__':
    app.run(debug=True)
