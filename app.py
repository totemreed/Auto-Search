from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Environment Variables (or you can hardcode the client's keys)
API_KEY = os.environ.get("API_KEY")
SEARCH_ENGINE_ID = os.environ.get("SEARCH_ENGINE_ID")


@app.route("/search", methods=["POST"])
def search():
    try:
        data = request.get_json()
        query = data.get("query")

        if not query:
            return jsonify({"error": "Missing 'query' in request body"}), 400

        google_url = "https://www.googleapis.com/customsearch/v1"
        filtered_items = []

        # ✅ Fetch 20 results in two requests (1–10, 11–20)
        for start in [1, 11]:
            params = {
                "key": API_KEY,
                "cx": SEARCH_ENGINE_ID,
                "q": query,
                "start": start
            }

            response = requests.get(google_url, params=params)
            response.raise_for_status()
            search_results = response.json()
            raw_items = search_results.get("items", [])

            for item in raw_items:
                clean_item = {
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "displayLink": item.get("displayLink"),
                    "snippet": item.get("snippet"),
                }

                # Optional image filter
                pagemap = item.get("pagemap", {})
                cse_image = pagemap.get("cse_image")
                if cse_image:
                    clean_item["image"] = cse_image[0].get("src")

                filtered_items.append(clean_item)

        result_data = {
            "query": query,
            "results": filtered_items
        }

        return jsonify(result_data), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        return jsonify({"error": "Internal server error", "details": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
