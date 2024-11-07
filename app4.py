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


#a route which only takes prompt in body no pdf 
@app.route("/inter" , methods=["POST"]) 
def inter():
    prompt = request.json['prompt']
    model= genai.GenerativeModel("gemini-1.5-pro",
                                generation_config={"response_mime_type": "application/json"},
                                system_instruction=""""
                                You are a gender-neutral interviewer. You are interviewing a candidate for a software engineering position. You can ask questions about their skills and experience.
                                the prompt will contain the details of the candidate and you have to ask questions based on that.
                                If details are not there ask general questions about the software engineering field minimum 10 questions favourable is more than that .
                                response = {
                                    questions:[
                                        {
                                            question:str,
                                            answer:str
                                        },
                                        {
                                        question:str,
                                        answer:str
                                        },
                                        {
                                        question:str,
                                        answer:str
                                        }
                                    ]
                                }
                                """)
    raw_response = model.generate_content([prompt ])
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
