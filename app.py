from flask import Flask, request, jsonify
import base64
from io import BytesIO
from PIL import Image
import openai
import os
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()

app = Flask(__name__)
openai.api_key = os.getenv('OPENAI_API_KEY')
CORS(app, resources={r"/*": {"origins": "*"}})

def analyze_images(front_image, back_image, weight, goal):
    try:
        # Create a prompt that includes the weight and goal
        prompt = f"""
        Analyze this person's body composition and provide:
        1. A detailed analysis of their physique, including strengths and areas for improvement
        2. A personalized workout plan based on their:
           - Current weight: {weight} kg
           - Goal: {goal}
        
        The workout plan should be structured with:
        - Clear section headers (e.g., "### 1. Upper Body Focus")
        - Specific exercises with sets and reps
        - Rest periods
        - Notes on form and technique
        """
        
        # Convert base64 images to PIL Images
        front_img = Image.open(BytesIO(base64.b64decode(front_image)))
        back_img = Image.open(BytesIO(base64.b64decode(back_image)))
        
        # Save images temporarily
        front_img.save("front.jpg")
        back_img.save("back.jpg")
        
        # Call OpenAI Vision API
        response = openai.ChatCompletion.create(
            model="gpt-4-vision-preview",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{front_image}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{back_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=2000
        )
        
        # Clean up temporary files
        os.remove("front.jpg")
        os.remove("back.jpg")
        
        # Parse the response to separate analysis and workout plan
        full_response = response.choices[0].message.content
        parts = full_response.split("###")
        
        analysis = parts[0].strip()
        workout_plan = "###" + "###".join(parts[1:]).strip() if len(parts) > 1 else ""
        
        return analysis, workout_plan
        
    except Exception as e:
        print(f"Error in analysis: {str(e)}")
        return None, None

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        
        if not data or 'front_image' not in data or 'back_image' not in data or 'weight' not in data or 'goal' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        
        front_image = data['front_image']
        back_image = data['back_image']
        weight = data['weight']
        goal = data['goal']
        
        analysis, workout_plan = analyze_images(front_image, back_image, weight, goal)
        
        if analysis is None or workout_plan is None:
            return jsonify({"error": "Failed to analyze images"}), 500
        
        return jsonify({
            "analysis": analysis,
            "workout_plan": workout_plan
        })
        
    except Exception as e:
        print(f"Error in endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/mealplan', methods=['POST'])
def mealplan():
    try:
        data = request.get_json()
        if not data or 'weight' not in data or 'goal' not in data:
            return jsonify({"error": "Missing required parameters"}), 400
        weight = data['weight']
        goal = data['goal']
        prompt = f"""
        Create a personalized meal plan for someone with:
        - Current weight: {weight} kg
        - Goal: {goal}
        The meal plan should include breakfast, lunch, dinner, and snacks, with macronutrient breakdowns and portion sizes.
        """
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        meal_plan = response.choices[0].message.content
        return jsonify({"meal_plan": meal_plan})
    except Exception as e:
        print(f"Error in mealplan endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
app.run(host="0.0.0.0", port=10000, debug=True)
