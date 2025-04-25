from flask import Flask, request, jsonify
from utils.data_processor import load_csv, summarize_data, generate_chart
import os
import shutil
import json
import sys
import logging

# Configure logging to use stderr instead of stdout
logging.basicConfig(stream=sys.stderr, level=logging.INFO)

app = Flask(__name__)

DATA_DIR = "data"

# Ensure the data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Copy the CSV file to the data directory if it doesn't exist there
def setup_data():
    source_file = "../BCAzureUsage 1.csv"
    target_file = os.path.join(DATA_DIR, "BCAzureUsage 1.csv")
    
    if os.path.exists(source_file) and not os.path.exists(target_file):
        shutil.copy(source_file, target_file)

# Run setup when the app starts
with app.app_context():
    setup_data()
    logging.info("Data setup complete")

@app.route("/", methods=["GET"])
def home():
    logging.info("Home endpoint accessed")
    return jsonify({
        "status": "Azure Usage MCP Server is running",
        "endpoints": ["/ask"],
        "version": "1.0.0"
    })

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    logging.info(f"Received ask request: {data}")
    query = data.get("query", "")
    
    file_path = os.path.join(DATA_DIR, "BCAzureUsage 1.csv")
    if not os.path.exists(file_path):
        return jsonify({"error": "Dataset not found"}), 404

    df = load_csv(file_path)
    
    # A simplified version of search/context logic
    response = {
        "query": query,
        "summary": summarize_data(df),
        "head": df.head(5).to_dict(orient="records"),
        "columns": df.columns.tolist()
    }
    
    # Add cost information if relevant
    if "cost" in query.lower() and 'Cost' in df.columns:
        total_cost = df['Cost'].sum()
        avg_cost = df['Cost'].mean()
        response["total_cost"] = f"${total_cost:.2f}"
        response["average_cost"] = f"${avg_cost:.2f}"
        
        # Add top services by cost
        top_services = df.groupby('ServiceName')['Cost'].sum().sort_values(ascending=False).head(5)
        response["top_services"] = [{
            "name": service,
            "cost": f"${cost:.2f}"
        } for service, cost in top_services.items()]
    
    # Add region information if relevant
    if any(term in query.lower() for term in ["region", "location", "geography"]) and 'ServiceRegion' in df.columns:
        top_regions = df.groupby('ServiceRegion')['Cost'].sum().sort_values(ascending=False).head(5)
        response["top_regions"] = [{
            "name": region,
            "cost": f"${cost:.2f}"
        } for region, cost in top_regions.items()]
        response["chart_path"] = generate_chart(df, 'ServiceRegion', 'Cost')
    
    # Add service information if relevant
    if any(term in query.lower() for term in ["service", "resource", "usage"]) and 'ServiceName' in df.columns:
        service_counts = df['ServiceName'].value_counts().head(5)
        response["top_services_by_count"] = [{
            "name": service,
            "count": count
        } for service, count in service_counts.items()]
    
    # Include basic visual if available and not already set
    if "chart_path" not in response and "ServiceName" in df.columns and "Cost" in df.columns:
        response["chart_path"] = generate_chart(df, 'ServiceName', 'Cost')
    
    return jsonify(response)

if __name__ == "__main__":
    # Configure Flask logging to use stderr
    import logging
    from flask.logging import default_handler
    
    # Remove default handler and add our own stderr handler
    app.logger.removeHandler(default_handler)
    stderr_handler = logging.StreamHandler(sys.stderr)
    app.logger.addHandler(stderr_handler)
    app.logger.setLevel(logging.INFO)
    
    # Disable Flask's default banner
    import flask.cli
    flask.cli.show_server_banner = lambda *x, **y: None
    
    # Log startup info to stderr
    logging.info("Starting Azure Usage MCP Server on port 8000")
    
    # Run the Flask app with minimal output
    app.run(host="127.0.0.1", port=8000, debug=True, use_reloader=False)
