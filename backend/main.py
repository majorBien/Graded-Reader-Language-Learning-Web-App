from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# DeepSeek API key
DEEPSEEK_API_KEY = "your-api-key" # Put you API key here
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

# generating text with deepSeek API function
def generate_text_with_deepseek(prompt, level, word_limit, language):
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    # Adjust prompt to level of the language
    system_prompt = (
        f"You are a helpful assistant that generates graded readers. "
        f"Generate a text in {language} at {level} level. "
        f"The text should be no longer than {word_limit} words. "
        f"Use simple vocabulary and grammar suitable for {level} level."
        f"Do not include any introductory text like 'もちろん！以下は...'."
    )
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": int(word_limit) * 2,  # conversion of words to tokens
        "temperature": 0.7,  # control creativity (lower value is more deterministic)
        "top_p": 0.9,  # use nucleus sampling
        "frequency_penalty": 0.5,  # avoid repeating words
        "presence_penalty": 0.5  # avoid repeating of topics
    }
    response = requests.post(DEEPSEEK_API_URL, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        raise Exception(f"Błąd API: {response.status_code}, {response.text}")

# endpoint for reader generation
@app.route('/generate_text', methods=['POST'])
def generate_text_endpoint():
    try:
        # dwonload frontend data
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "Brak danych"}), 400

        prompt = data.get("prompt")
        level = data.get("level")
        word_limit = data.get("wordLimit")
        language = data.get("language")

        # data validation
        if not all([prompt, level, word_limit, language]):
            return jsonify({"success": False, "error": "Brak wymaganych pól"}), 400

        # check if words limit is a number
        try:
            word_limit = int(word_limit)
        except ValueError:
            return jsonify({"success": False, "error": "wordLimit musi być liczbą"}), 400

        # generate text with deep seek API
        generated_text = generate_text_with_deepseek(prompt, level, word_limit, language)

        # Find the answer with generated text
        return jsonify({
            "success": True,
            "text": generated_text
        })
    except Exception as e:
        # handle error and send response
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)