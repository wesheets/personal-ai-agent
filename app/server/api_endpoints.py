#!/usr/bin/env python3
import json
import os
from flask import Flask, jsonify, send_from_directory

# Assuming the script is in personal-ai-agent/app/server/
# and justification_graph_data.json is in personal-ai-agent/app/memory/
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..")) # This should point to app/
MEMORY_DIR = os.path.join(BASE_DIR, "memory")
GRAPH_DATA_PATH = os.path.join(MEMORY_DIR, "justification_graph_data.json")

app = Flask(__name__)

@app.route("/api/justification-graph", methods=["GET"])
def get_justification_graph_data():
    """Serves the justification_graph_data.json file."""
    if not os.path.exists(GRAPH_DATA_PATH):
        return jsonify({"error": "Graph data file not found."}), 404
    try:
        # Serve the file directly if it's static JSON data
        # For more complex scenarios, you might load and process it
        return send_from_directory(MEMORY_DIR, "justification_graph_data.json", as_attachment=False, mimetype="application/json")
    except Exception as e:
        print(f"Error serving graph data: {e}")
        return jsonify({"error": f"Could not serve graph data: {str(e)}"}), 500

# Placeholder for other API endpoints
@app.route("/api/loop_status")
def get_loop_status():
    # Logic to fetch and return loop status from loop_context.json
    # This is just a placeholder from the original file
    loop_context_path = os.path.join(MEMORY_DIR, "loop_context.json")
    if os.path.exists(loop_context_path):
        try:
            with open(loop_context_path, "r") as f:
                context = json.load(f)
            return jsonify(context)
        except Exception as e:
            return jsonify({"error": f"Could not read loop context: {str(e)}"}), 500
    return jsonify({"status": "unknown", "message": "Loop context not found."}), 404

# New Replay Endpoint
REPLAY_DATA_DIR = os.path.join(BASE_DIR, "data", "replay_data") # app/data/replay_data

@app.route("/api/replay/loop/<loop_id>", methods=["GET"])
def get_loop_replay_data(loop_id):
    """
    Retrieves historical loop data for a specific loop_id
    for step-by-step replay visualization.
    """
    # Placeholder logic: In a real implementation, this would involve:
    # 1. Validating loop_id format.
    # 2. Constructing paths to relevant log files (loop_trace, justifications, reflections, emotion, governance).
    #    These might be within MEMORY_DIR or a dedicated REPLAY_DATA_DIR if specific loop data is archived.
    # 3. Reading and parsing these files.
    # 4. Correlating data based on loop_id and timestamps.
    # 5. Structuring the data into a step-by-step format for the UI.

    # For now, let's assume we look for a file named {loop_id}_replay.json in REPLAY_DATA_DIR
    # This is a simplified placeholder for demonstration.
    replay_file_path = os.path.join(REPLAY_DATA_DIR, f"{loop_id}_replay.json")

    # The REPLAY_DATA_DIR should exist if setup steps were followed.
    # We don't create it here as that's not the API's role during a GET request.

    if os.path.exists(replay_file_path):
        try:
            with open(replay_file_path, "r") as f:
                replay_data = json.load(f)
            return jsonify(replay_data)
        except Exception as e:
            return jsonify({"error": f"Could not read or parse replay data for loop_id {loop_id}: {str(e)}"}), 500
    else:
        # Placeholder response if specific replay data file isn't found
        # In a real scenario, you'd dynamically build this from various logs.
        sample_replay_step = {
            "step_number": 1,
            "timestamp": "2025-05-10T00:00:00Z",
            "active_agent": "PlaceholderAgent",
            "action": "Placeholder Action",
            "justification": f"Data for loop_id {loop_id} not found or not yet processed. This is a sample response.",
            "emotional_context": {"emotion": "neutral", "intensity": 0.0},
            "governance_influence": "None",
            "raw_data_references": []
        }
        return jsonify({
            "loop_id": loop_id,
            "status": "Data not found or not yet processed",
            "replay_steps": [sample_replay_step]
        }), 404

if __name__ == "__main__":
    print(f"Graph data path: {GRAPH_DATA_PATH}")
    print(f"Memory directory: {MEMORY_DIR}")
    # This is for running the Flask development server.
    # In a production setup, a proper WSGI server like Gunicorn would be used.
    # The agent environment might not run this directly but use the Flask app object.
    # For the purpose of this batch, defining the endpoints is the key part.
    # The actual running of the server to verify UI rendering is conceptual for the agent.
    print("api_endpoints.py defined. To run for testing: flask run --port=5001 (or your chosen port)")
    # app.run(host="0.0.0.0", port=5001, debug=True) # Agent should not run this directly

