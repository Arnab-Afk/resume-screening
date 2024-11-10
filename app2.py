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
from flask_cors import CORS

app = Flask(__name__)
load_dotenv() 
CORS(app)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if GOOGLE_API_KEY is None:
    raise ValueError("No GOOGLE_API_KEY found in environment variables")
genai.configure(api_key=GOOGLE_API_KEY)



@app.route("/recipie", methods=["POST"])
def recipie():
    if request.method == "POST":
        food_item = request.form.get("food_item")
        quantity = request.form.get("quantity")
        
        # Ensure food_item and quantity are of the correct types
        if not food_item or not quantity:
            return jsonify({"error": "food_item must be a string"}), 400
        if not isinstance(quantity, str):
            return jsonify({"error": "quantity must be a string"}), 400
        model=genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"},
                                    system_instruction="""You are a recipie generator bot. you have to suggest recipies based on the letfover item provided in the prompt along with its quantity.
                                    Try to suggest recipies that are easy to make and use the ingredient provided in the prompt. Try to suggest indian recipies first and then move on towards others.
                                    response={
                                        recipie{
                                            title :str,
                                            description :str,
                                            ingredients :[
                                                {
                                                    ingredient_name: str,
                                                    quantity: str
                                                }
                                            ],
                                            steps:[step1 , step2 ,....]
                                        },
                                        recipie{
                                            title :str,
                                            description :str,
                                            ingredients :[
                                                {
                                                    ingredient_name: str,
                                                    quantity: str
                                                }
                                            ],
                                            steps:[step1 , step2 ,....]
                                        },
                                        recipie{
                                            title :str,
                                            description :str,
                                            ingredients :[
                                                {
                                                    ingredient_name: str,
                                                    quantity: str
                                                }
                                            ],
                                            steps:[step1 , step2 ,....]
                                        }
                                    }
                                    """)
        raw_response = model.generate_content([food_item, quantity])
        response = json.loads(raw_response.text)
        return response

@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if request.method == "POST":
        keywords=request.args.get("keywords")
        if (not keywords):
            pdf_file = request.files["pdf_file"]
            temp_file_path = os.path.join(os.getcwd(), pdf_file.filename)
            pdf_file.save(temp_file_path)
            
            images = pdf2image.convert_from_path(temp_file_path, dpi=200)[:2]
            image_files = []
            num_pages=len(images)
            model = genai.GenerativeModel("gemini-1.5-pro",
                                generation_config={"response_mime_type": "application/json"},
                                system_instruction="You are a resume parser agent you will be provided a image of a resume and just give the details from the resume.")
            prompt = """Provide the name skills and languages and suggestions how this resume can be improved from the image  the 1st image is 1st page and 2nd image is second page of resume:

                        response = {
                        'name': str,
                        'email':str,
                        'phone':str,
                        'description':str,
                        'professional_experience_in_years':int,
                        
                        'skills':list[skills],
                        'languages':list[languages],
                        'education':list[education],
                        'experience':list[experience],
                        'projects':list[projects],
                        'certifications':list[certifications],
                        'achievements':list[achievements],
                        'is_student':bool,
                        'is_fresher':bool,
                        'is_experienced':bool,}
                        Return:response"""
            for i, image in enumerate(images):
                image_file = f"page_{i+1}.jpg"
                image.save(image_file, "JPEG")
                image_files.append(os.path.join(os.getcwd(), image_file))
            try:
                if num_pages == 2:
                    img_page1 = genai.upload_file(path=image_files[0], display_name=f"Page 1")
                    img_page2 = genai.upload_file(path=image_files[1], display_name=f"Page 2")
                    raw_response = model.generate_content([prompt , img_page1 , img_page2])
                else:
                    img_page1 = genai.upload_file(path=image_files[0], display_name=f"Page 1")
                    raw_response = model.generate_content([prompt , img_page1])
                print(img_page1)
                response = json.loads(raw_response.text)
            finally:
                # Delete temporary files
                os.remove(temp_file_path)
                for image_file in image_files:
                    os.remove(image_file)  
                
            return response
        else:
            pdf_file = request.files["pdf_file"]
            temp_file_path = os.path.join(os.getcwd(), pdf_file.filename)
            pdf_file.save(temp_file_path)
            
            images = pdf2image.convert_from_path(temp_file_path, dpi=200)[:2]
            image_files = []
            num_pages=len(images)
            model = genai.GenerativeModel("gemini-1.5-flash-latest",
                                generation_config={"response_mime_type": "application/json"},
                                system_instruction="You are a resume parser agent you will be provided a image of a resume and just give the requirements from the resume and nothing else.")
            prompt = f"""Provide suggestions how this resume can be improved for the specific job role {keywords} and what is required for the specific job role and a overall how much the person is suitable for that role according to his resume.
                        response={{
                        improvement:["improvement1" , improvement2 ....],
                        summary:"summary of the entire report",
                        requirements:["requirement1", "requirement2", ....],
                        overallview:["view1","view2", .....]
                        }}
                        Return:response"""
            for i, image in enumerate(images):
                image_file = f"page_{i+1}.jpg"
                image.save(image_file, "JPEG")
                image_files.append(os.path.join(os.getcwd(), image_file))
            try:
                if num_pages == 2:
                    img_page1 = genai.upload_file(path=image_files[0], display_name=f"Page 1")
                    img_page2 = genai.upload_file(path=image_files[1], display_name=f"Page 2")
                    raw_response = model.generate_content([prompt , img_page1 , img_page2])
                else:
                    img_page1 = genai.upload_file(path=image_files[0], display_name=f"Page 1")
                    raw_response = model.generate_content([prompt , img_page1])
                print(img_page1)
                response = json.loads(raw_response.text)
            finally:
                # Delete temporary files
                os.remove(temp_file_path)
                for image_file in image_files:
                    os.remove(image_file)  
                
            return response
            
    return jsonify({"message": "Invalid request"})

if __name__ == "__main__":
    app.run(debug=True)
