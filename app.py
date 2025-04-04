from flask import Flask, request, jsonify, render_template
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoConfig
import numpy as np
from scipy.special import softmax
import logging 

app = Flask(__name__)

#Configure logging
#logging.basicConfig(level=logging.INFO)

# --- Load Model --- 
try:
    MODEL = f"cardiffnlp/twitter-roberta-base-sentiment-latest"
    tokenizer = AutoTokenizer.from_pretrained(MODEL)
    config = AutoConfig.from_pretrained(MODEL)
    model = AutoModelForSequenceClassification.from_pretrained(MODEL)
    app.logger.info(f"Model {MODEL} loaded successfully.")
except Exception as e:
    app.logger.error(f"Error loading model: {e}")
    
    exit()
# --- End Load Model ---

# --- Preprocess Function 
def preprocess(text):
    new_text = []
    for t in text.split(" "):
        t = '@user' if t.startswith('@') and len(t) > 1 else t
        t = 'http' if t.startswith('http') else t
        new_text.append(t)
    return " ".join(new_text)
# --- End Preprocess Function ---

# --- Analyze Sentiment Function ---
def analyze_sentiment(text):
    try:
        text_processed = preprocess(text)
        encoded_input = tokenizer(text_processed, return_tensors='pt')
        model.eval()
        output = model(**encoded_input)
        scores = output[0][0].detach().numpy()
        scores = softmax(scores)

        ranking = np.argsort(scores)
        ranking = ranking[::-1]

        result = {}
        for i in range(scores.shape[0]):
            label = config.id2label[ranking[i]]
            score = scores[ranking[i]]
            result[label] = np.round(float(score), 4)
        return result
    except Exception as e:
        app.logger.error(f"Error during sentiment analysis: {e}")
        return {"error": "Analysis failed", "details": str(e)}
# --- End Analyze Sentiment Function ---

# --- API Endpoint --- 
@app.route('/analyze', methods=['POST'])
def analyze_api(): 
    app.logger.info("Received request for /analyze")
    data = request.get_json()
    if not data:
        app.logger.warning("Request received with no JSON data.")
        return jsonify({'error': 'Bad Request: No JSON data received'}), 400

    tweet = data.get('tweet')
    if tweet:
        app.logger.info(f"Analyzing tweet: {tweet[:50]}...") # Log snippet
        sentiment = analyze_sentiment(tweet)
        if "error" in sentiment:
             app.logger.error(f"Analysis failed for tweet: {tweet[:50]}...")
             return jsonify(sentiment), 500 # Internal Server Error
        else:
            app.logger.info(f"Analysis successful: {sentiment}")
            return jsonify(sentiment)
    else:
        app.logger.warning("Request received but 'tweet' key missing or empty.")
        return jsonify({'error': 'No tweet provided in JSON payload'}), 400
# --- End API Endpoint ---

# ---Frontend Route ---
@app.route('/')
def index():
    """Serves the main HTML frontend page."""
    app.logger.info("Serving index.html")
    return render_template('index.html')
# --- End Frontend Route ---

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)