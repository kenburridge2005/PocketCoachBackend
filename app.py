import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import openai

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

openai.api_key = os.environ.get("OPENAI_API_KEY")

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
        weight = request.form.get("weight")
        goal = request.form.get("goal")
        front_image = request.files.get("front_image")
        back_image = request.files.get("back_image")

        prompt = (
            f"User's weight: {weight} kg. Goal: {goal}.\n"
            "Based on the user's front and back body photos (not shown here), provide a fitness analysis and a detailed, actionable workout plan."
        )

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
            f"You are a certified fitness nutrition coach. Create a 1-week meal plan for someone who wants to {goal}. "
            f"{'Calorie target: ' + calories + '.' if calories else ''} "
            f"{'Dietary preferences/allergies: ' + preferences + '.' if preferences else ''} "
            "The plan should include breakfast, lunch, dinner, and snacks for each day. Make it realistic, healthy, and easy to follow. Format as Markdown."
        )

        mealplan = call_openai(prompt, max_tokens=1200)
        return jsonify({"mealplan": mealplan}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
