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


@app.route("/", methods=["GET"])
def home():
    return "Welcome to the home page of the API"

@app.route("/recipie", methods=["POST"])
def recipie():
    if request.method == "POST":
        food_item = request.form.get("food_item")
        quantity = request.form.get("quantity")
        
        # Ensure food_item and quantity are of the correct types
       
        
        model = genai.GenerativeModel("gemini-1.5-flash", generation_config={"response_mime_type": "application/json"},
                                      system_instruction="""You are a recipie generator bot. you have to suggest recipies based on the letfover item provided in the prompt along with its quantity.
                                      Try to suggest multiple recipies that are easy to make and use the ingredient provided in the prompt. Try to suggest indian recipies first and then move on towards others.minimum 3 recipies are required.
                                      response={
                                          {
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
                                          {
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
                                          {
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
                                      }"""
                                     )
        
        raw_response = model.generate_content([food_item, quantity])
        
        # Print raw_response.text for debugging
        print(raw_response.text)
        
        try:
            response = json.loads(raw_response.text)
        except json.JSONDecodeError as e:
            return jsonify({"error": "Invalid JSON response from model", "details": str(e)}), 500
        
        return response





if __name__ == "__main__":
    app.run(debug=True)