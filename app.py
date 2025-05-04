from flask import Flask, request, jsonify
from openai import OpenAI
import os

client = OpenAI()
app = Flask(__name__)
OpenAI.api_key = os.environ.get("OPENAI_API_KEY")  # Use environment variable for security

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        print("Received /analyze POST request")
        data = request.json
        print(f"Request data keys: {list(data.keys()) if data else 'No data received'}")
        front_image = data['front_image']
        back_image = data['back_image']

        prompt = (
            "You are a fitness coach. Analyze the following two images of a person's body (front and back). "
            "Describe their strengths, weaknesses, and recommend specific workouts to address their weaknesses. "
            "Be specific."
        )

        response = client.chat.completions.create(
            model="gpt-4.1",  # Use the correct model name you have access to
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{front_image}"}},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{back_image}"}}
                ]}
            ],
            max_tokens=500
        )

        print("OpenAI response received")
        return jsonify({"analysis": response.choices[0].message.content})
    except Exception as e:
        print(f"Error in /analyze: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
