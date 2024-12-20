from flask import Flask, request, jsonify
import pdf2image
import io
import google.generativeai as genai
import tempfile
import os
import json
import dataclasses
import requests
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



#a route which takes string and processes it 
@app.route("/analyseFood", methods=["POST"])
def analyseFood():
    if request.method == "POST":
        food_item = request.json['food_item']
        model = genai.GenerativeModel("gemini-1.5-flash",
                                generation_config={"response_mime_type": "application/json"},
                                system_instruction="""You are string  analyser bot. You will be provided the details of a food item provided in the prompt.
                                everything will be provided in the prompt you just have to segregate the details and provide the details in the response.
                                 response={
                                    food_item: str,
                                    expiry_date: str,
                                    quantity: str,
                                    phone_number str
                                 }""")
        raw_response = model.generate_content([food_item])
        response = json.loads(raw_response.text)
    return response



VERIFY_TOKEN = "arnab"
TARGET_ENDPOINT = ''  # Replace with your target endpoint

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # WhatsApp webhook verification
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        if token == VERIFY_TOKEN:
            return str(challenge), 200
        else:
            return "Verification token mismatch", 403
    
    if request.method == 'POST':
        data = request.json
        
        if data:
            print(data)  # Print the entire data for debugging
            
            # Extract the text body
            try:
                text_body = data['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
                entry = data['entry'][0]
                changes = entry['changes'][0]
                value = changes['value']
                wa_id = value['contacts'][0]['wa_id']
                print(f"Text Body: {text_body}")
                
                # Check if the text body matches the pattern /add something
                if text_body.startswith('/add '):
                    content = text_body[5:]  # Extract the content after /add
                    print(f"Content to add: {content}")
                    
                    # Make an HTTP POST request to the target endpoint with the content
                    model = genai.GenerativeModel("gemini-1.5-flash",
                                generation_config={"response_mime_type": "application/json"},
                                system_instruction="""You are string  analyser bot. You will be provided the details of a food item provided in the prompt.
                                everything will be provided in the prompt you just have to segregate the details and provide the details in the response.
                                 response={
                                    food_item: str,
                                    expiry_date: str,
                                    quantity: str,
                                    phone_number str
                                 }""")
                    raw_response = model.generate_content([content + wa_id])
                    response = json.loads(raw_response.text)
                    food_item = response['food_item']
                    expiry_date = response['expiry_date']
                    quantity = response['quantity']
                    phone_number = response['phone_number']
                    response = requests.post("https://annapurna.featurehive.live/v1/household/add-products", json={food_item: food_item, expiry_date: expiry_date, quantity: quantity, phone_number: phone_number})
                    print(response)
            except (KeyError, IndexError) as e:
                print(f"Error extracting text body: {e}")
                return "Error", 400
        else:
            print("No data")
            return "Error", 400
        
        return "Success", 200
# a route which takes in food item and its quantity and gives quick recipies using it

@app.route("/recipie" , methods=['POST'])
def recipie():
    if request.method=="POST":
        food_item= request.json['food_item']
        quantity=request.json['quantity']
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
        raw_response= model.generate_content([food_item, quantity])
        response = json.loads(raw_response.text)
    return raw_response

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
                try:
                    response = json.loads(raw_response.text)
                except json.JSONDecodeError as e:
                    print("JSONDecodeError:", e)
                    response = {"error": "Response not in expected JSON format."}
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
                        report:// this is a example"ATS Analysis and Feedback for Kunal Chaturvedi

                        Overall Score: 85% (out of 100)
                        
                        Feedback: Kunal has a very strong resume for this Software Developer role. His technical skills, project experience, and demonstrated proficiency in relevant technologies align well with the job requirements. With a few minor adjustments, his resume will be even more compelling.
                        
                        Section-Specific Recommendations:
                        
                        1. Contact Information (10%):
                        
                        Points: 10/10
                        
                        Changes:
                        
                        Keep it as is. The inclusion of LinkedIn is a good addition for this role.
                        
                        2. Education (15%):
                        
                        Points: 15/15
                        
                        Changes:
                        
                        Highlight Relevant Courses: Emphasize courses like Algorithms, Data Structures, Compiler Design, and any relevant programming courses related to the job description.
                        
                        Project/Experience: Include relevant projects done during your studies, especially those focused on software development.
                        
                        3. Experience (30%):
                        
                        Points: 28/30
                        
                        Changes:
                        
                        Prioritize Software Development Experience: Focus on experiences where you developed software, integrated systems, or worked on projects aligned with the job description.
                        
                        Quantify Impact: Use numbers to showcase your achievements. For example, "Developed a cost-optimized solution for log retrieval, resulting in a 20% reduction in retrieval time."
                        
                        Highlight Relevant Technologies: Mention keywords from the job description, such as "Agile frameworks," "JavaScript," and "Python."
                        
                        4. Projects (15%):
                        
                        Points: 15/15
                        
                        Changes:
                        
                        Prioritize Software Development Projects: Emphasize projects like "Eventio," "Sanjeevni," "AudiLook," and "GoSafe" as they showcase your technical skills and relevant programming experience.
                        
                        Clearer Descriptions: Provide brief and clear descriptions of your project contributions, highlighting the technologies used and the outcome.
                        
                        5. Skills (15%):
                        
                        Points: 14/15
                        
                        Changes:
                        
                        Organize by Category: Group skills logically, separating programming languages, development technologies, and design tools.
                        
                        Highlight Relevant Skills: Prioritize skills like Python, JavaScript, React.js, Next.js, React-Native, Node.js, Express.js, MongoDB, PostgreSQL, MySQL, and Agile methodologies.
                        
                        Add Specific Skills: Mention skills like debugging, troubleshooting, and software integration, if applicable.
                        
                        6. Achievements (15%):
                        
                        Points: 13/15
                        
                        Changes:
                        
                        Focus on Software Development Achievements: Highlight achievements that demonstrate your technical expertise and software development accomplishments.
                        
                        Contextualize: Briefly explain how your achievements demonstrate your ability to build, implement, and improve software systems.
                        
                        Final Verdict:
                        
                        Kunal's resume is a strong match for this Software Developer position. His technical skills, project experience, and demonstrated proficiency in relevant technologies align very well with the job requirements.
                        
                        Final Fit Number: 8/10
                        
                        Interpretation: Kunal's resume is excellent for this job description. With a few minor changes, his resume should be ready to apply.
",                      
                        overall_score:int,
                        feedback:"feedback of the entire report",
                        interpretation:"interpretation of the entire report",
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
                try:
                    response = json.loads(raw_response.text)
                except json.JSONDecodeError as e:
                    print("JSONDecodeError:", e)
                    response = {"error": "Response not in expected JSON format."}
            finally:
                # Delete temporary files
                os.remove(temp_file_path)
                for image_file in image_files:
                    os.remove(image_file)  
                
            return response
            
    return jsonify({"message": "Invalid request"})

if __name__ == "__main__":
    app.run(debug=True)
