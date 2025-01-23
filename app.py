from flask import Flask, request, jsonify
from PyPDF2 import PdfReader
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

# Initialize Flask app and summarizer pipeline
app = Flask(__name__)
summarizer = pipeline("summarization")

# Function to extract text from PDF
def extract_text_from_pdf(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

# Function to extract text from URL
def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    return ' '.join([p.get_text() for p in soup.find_all('p')])

# Summarization endpoint
@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.get_json()
    
    text = data.get('text')
    url = data.get('url')
    file = data.get('file')
    
    # Check if URL is provided
    if url:
        text = extract_text_from_url(url)
    
    # Check if PDF file is provided
    if file:
        text = extract_text_from_pdf(file)
    
    # If text is provided directly
    if text:
        if len(text.split()) > 50:  # Adjust as needed
            summary = summarizer(text, max_length=150, min_length=50, do_sample=False)[0]['summary_text']
        else:
            summary = "The text is too short for summarization."
    else:
        summary = "No valid input provided."
    
    return jsonify({'summary': summary})

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
