import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai
from werkzeug.utils import secure_filename
from PIL import Image
import io
import base64

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set your OpenAI API key
openai.api_key = os.environ.get("OPENAI_API_KEY")

# Helper function to call OpenAI API
def call_openai(prompt, model="gpt-4o", max_tokens=800):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.7,
    )
    return response.choices[0].message["content"]

@app.route("/analyze", methods=["POST"])
def analyze():
    try:
        # Get data from request
        weight = request.form.get("weight")
        goal = request.form.get("goal")
        front_image = request.files.get("front_image")
        back_image = request.files.get("back_image")

        # Optionally, process images (e.g., save, analyze, etc.)
        # For now, just acknowledge receipt
        # You could convert images to base64 if you want to send them to OpenAI Vision models

        prompt = (
            f"User's weight: {weight} kg. Goal: {goal}.\n"
            "Based on the user's front and back body photos (not shown here), provide a fitness analysis and a detailed, actionable workout plan."
        )

        # Call OpenAI API
        analysis = call_openai(prompt)

        return jsonify({"analysis": analysis}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/mealplan", methods=["POST"])
def mealplan():
    try:
        data = request.get_json()
        goal = data.get("goal")
        preferences = data.get("preferences", "")
        calories = data.get("calories", "")

        prompt = (
            f"Create a 1-day meal plan for someone whose goal is '{goal}'. "
            f"Dietary preferences: {preferences}. "
            f"Calorie target: {calories} kcal. "
            "List meals with ingredients and approximate calories per meal."
        )

        mealplan = call_openai(prompt)

        return jsonify({"mealplan": mealplan}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
