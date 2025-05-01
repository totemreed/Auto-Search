from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
SEARCH_ENGINE_ID = os.getenv("SEARCH_ENGINE_ID")

@app.route("/search", methods=["POST"])
def search_google():
    data = request.get_json()
    query = data.get("query")

    if not query:
        return jsonify({"error": "Missing 'query' in request body"}), 400

    try:
        response = requests.get(
            "https://www.googleapis.com/customsearch/v1",
            params={
                "key": GOOGLE_API_KEY,
                "cx": SEARCH_ENGINE_ID,
                "q": query
            }
        )
        response.raise_for_status()
        search_data = response.json()

        results = []
        for item in search_data.get("items", []):
            results.append({
                "title": item.get("title"),
                "link": item.get("link"),
                "displayLink": item.get("displayLink"),
                "snippet": item.get("snippet"),
                "image": item.get("pagemap", {}).get("cse_image", [{}])[0].get("src", "")
            })

        return jsonify({
            "query": query,
            "results": results
        })

    except Exception as e:
        print("🔴 Google Search API Error:", str(e))
        return jsonify({
            "error": "Internal Server Error",
            "details": str(e)
        }), 500
