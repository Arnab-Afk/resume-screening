from flask import Flask, request, jsonify
import google.generativeai as genai
import os

app = Flask(__name__)
KEY=os.getenv('API_KEY')
# Configure the Generative AI API
genai.configure(api_key=KEY)

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
    file_path = os.path.join("uploads", file.filename)
    file.save(file_path)

    try:
        # Upload the file to Google Generative AI
        myfile = genai.upload_file(file_path)
        print(f"{myfile=}")

        # Initialize the Generative Model
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Generate content based on the audio file
        result = model.generate_content([myfile, " is this corerct grammar ? if not fix it and  please dont insert any asterisks or special characters."])
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
    # Ensure the uploads directory exists
    if not os.path.exists("uploads"):
        os.makedirs("uploads")

    # Run the Flask app
    app.run(debug=True)
