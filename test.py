from flask import Flask, request, jsonify
import pdf2image
import io
import google.generativeai as genai
import tempfile
import os
import json
import dataclasses
import typing_extensions as typing
from dotenv import load_dotenv
app = Flask(__name__)
load_dotenv() 
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise ValueError("No GOOGLE_API_KEY found in environment variables")
genai.configure(api_key=GOOGLE_API_KEY)

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            # Create a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            # Save the uploaded file to the temporary file
            file.save(temp_file.name)
            # Upload the file to GenAI
            md_file = genai.upload_file(
                path=temp_file.name,  # Pass the temporary file path
                display_name="Starred Repos Content",
                mime_type="text/markdown"
            )
            # Close and delete the temporary file
            temp_file.close()
            os.unlink(temp_file.name)
            return jsonify({'message': 'File uploaded successfully', 'md_file': md_file})
        else:
            return jsonify({'error': 'No file provided'})

if __name__ == '__main__':
    app.run(debug=True)