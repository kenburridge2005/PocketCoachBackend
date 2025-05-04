from flask import Flask, request, jsonify
import openai
import os

app = Flask(__name__)
openai.api_key = os.environ.get("OPENAI_API_KEY")  # Use environment variable for security

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    front_image = data['front_image']
    back_image = data['back_image']

    prompt = (
        "You are a fitness coach. Analyze the following two images of a person's body (front and back). "
        "Describe their strengths, weaknesses, and recommend specific workouts to address their weaknesses. "
        "Be specific and encouraging."
    )

    response = openai.chat.completions.create(
        model="gpt-4-vision",  # Updated model name
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": [
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{front_image}"}},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{back_image}"}}
            ]}
        ],
        max_tokens=500
    )

    return jsonify({"analysis": response.choices[0].message.content})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
