# Import the necessary modules 
import os
from flask import Flask, render_template,  send_from_directory #type: ignore 

app = Flask(__name__)

# get the absolute path and the files in the directory
@app.route("/")
def index():
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, "cms", "data")
    print('This is the data dir', data_dir)
    files = [os.path.basename(path) for path in os.listdir(data_dir)]
    return render_template('index.html', files=files)

# Read the content of each file
@app.route("/<filename>")
def file_content(filename):
    root = os.path.abspath(os.path.dirname(__file__))
    data_dir = os.path.join(root, "cms", "data")
    return send_from_directory(data_dir, filename)

# Run the application
if __name__ == "__main__":
    app.run(debug=True, port=5003)
