from app import app  # noqa: F401

# This file is set up to make the Flask application run properly
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
