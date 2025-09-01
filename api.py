from flask import Flask, request, jsonify, send_from_directory
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs

app = Flask(__name__, static_folder='.')

# 🔑 Replace with your YouTube API key
YOUTUBE_API_KEY = "AIzaSyBx-xlPrmOpO4zo0uBuYvu13R_H-2iz5F0"

# 🔹 Function to extract video ID from a YouTube URL
def get_video_id(youtube_url):
    parsed_url = urlparse(youtube_url)
    if parsed_url.hostname == "youtu.be":
        return parsed_url.path[1:]
    if parsed_url.hostname in ["www.youtube.com", "youtube.com"]:
        if parsed_url.path == "/watch":
            return parse_qs(parsed_url.query).get("v", [None])[0]
        elif parsed_url.path.startswith("/embed/") or parsed_url.path.startswith("/v/"):
            return parsed_url.path.split("/")[2]
    return None

# 🔹 Serve index.html
@app.route("/")
def home():
    return send_from_directory('.', 'index.html')

# 🔹 API endpoint to get video tags
@app.route("/get_tags", methods=["GET"])
def get_tags():
    youtube_url = request.args.get("url")
    if not youtube_url:
        return jsonify({"error": "No URL provided"}), 400

    video_id = get_video_id(youtube_url)
    if not video_id:
        return jsonify({"error": "Invalid YouTube URL"}), 400

    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request_video = youtube.videos().list(
            part="snippet",
            id=video_id
        )
        response = request_video.execute()

        if not response["items"]:
            return jsonify({"error": "Video not found"}), 404

        video_data = response["items"][0]["snippet"]
        title = video_data["title"]
        tags = video_data.get("tags", [])

        return jsonify({
            "video_title": title,
            "tags": tags
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
