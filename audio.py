from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)

# Get the API key from environment variables
API_KEY = os.getenv('API_KEY')
if not API_KEY:
    raise ValueError("No API_KEY found in environment variables")

# Configure the Generative AI API
genai.configure(api_key=API_KEY)

# Define the route for file upload
@app.route('/upload', methods=['POST'])
def upload_file():
    # Check if the post request has the file part
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400

    file = request.files['file']

    # If the user does not select a file, the browser submits an empty file without a filename
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Save the file temporarily
    uploads_dir = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(uploads_dir):
        os.makedirs(uploads_dir)

    file_path = os.path.join(uploads_dir, file.filename)
    file.save(file_path)

    try:
        # Upload the file to Google Generative AI
        myfile = genai.upload_file(file_path)
        print(f"{myfile=}")

        # Initialize the Generative Model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate content based on the audio file
        result = model.generate_content([myfile, "Is this correct grammar? If not, fix it and please don't insert any asterisks or special characters."])
        print(f"{result.text=}")

        # Return the result
        return jsonify({"description": result.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # Clean up: remove the uploaded file
        if os.path.exists(file_path):
            os.remove(file_path)

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000)
