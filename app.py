# Import the necessary modules 
import os
from functools import wraps
from flask import Flask, render_template,  send_from_directory, redirect, url_for, flash, request, session #type: ignore
from markdown import markdown #type: ignore

app = Flask(__name__)
app.secret_key = 'secret'

def user_signed_in():
    return 'username' in session

def require_signed_in_user(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        if not user_signed_in():
            flash("You must be signed in to do that.")
            return redirect(url_for('show_signin_form'))

        return func(*args, **kwargs)

    return decorated_function

# set the absolute path prior to starting the program.
def get_data_path():
    if app.config['TESTING']:
        return os.path.join(os.path.dirname(__file__), 'tests', 'data')
    else:
        return os.path.join(os.path.dirname(__file__), 'cms/data')

# get the absolute path and the files in the directory
@app.route("/")
def index():
    data_dir = get_data_path()
    files = [os.path.basename(path) for path in os.listdir(data_dir)]
    return render_template('index.html', files=files)

# Read the content of each file and return it only if available.
@app.route("/<filename>")
def file_content(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)
    
    if os.path.isfile(file_path):
        if file_path.endswith('md'):
            # Open and read the file content as a string
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            # Convert Markdown content to HTML
            return markdown(content)
        else:
            return send_from_directory(data_dir, filename)
    else:
        flash(f"{filename} does not exist.")
        return redirect(url_for('index'))

# Editing the content of a file
@app.route("/<filename>/edit")
@require_signed_in_user
def edit(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
        return render_template('edit.html', filename=filename, content=content)
    else:
        flash(f"{filename} does not exist.")
        return redirect(url_for('index'))
    
# Saving the content of a file
@app.route("/<filename>", methods=['POST'])
@require_signed_in_user
def save_file(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    # requesting the value of the form that was submitted, updating the old document.
    content = request.form['content'] # very important
    with open(file_path, 'w') as file:
        file.write(content)
    
    flash(f"{filename} has been updated.")
    return redirect(url_for('index'))

# Adding a new document
@app.route("/new_document")
@require_signed_in_user
def new_document():
    return render_template('new_document.html')

@app.route("/create", methods=['POST'])
@require_signed_in_user
def create_document():
    # requesting the value of the document that was submitted.
    new_doc = request.form.get('filename', "").strip()
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, new_doc)

    if len(new_doc) == 0:
        flash("A name is required.")
        return render_template('new_document.html'), 422
    elif os.path.exists(file_path):
        flash(f"{new_doc} already exists.")
        return render_template('new_document.html'), 422
    else:
        with open(file_path, 'w') as file:
            file.write("")
        flash(f"{new_doc} has been created.")
        return redirect(url_for('index'))

# Deleting a file 
@app.route("/<filename>/delete", methods=['POST'])
@require_signed_in_user
def delete_file(filename):
    data_dir = get_data_path()
    file_path = os.path.join(data_dir, filename)

    if os.path.isfile(file_path):
        os.remove(file_path)
        flash(f"{filename} has been deleted.")
    else:
        flash(f"{filename} does not exist.")

    return redirect(url_for('index'))

# Signing in into CMS
@app.route("/users/signin", methods=['GET'])
def show_signin_form():
    return render_template('signin.html')

# Validating username and password
@app.route("/users/signin", methods=['POST'])
def signin():
    username = request.form.get('username')
    password = request.form.get('password')

    if username == "admin" and password == "secret":
        session['username'] = username
        flash("Welcome!")
        return redirect(url_for('index'))
    else:
        flash("Invalid credentials")
        return render_template('signin.html'), 422

@app.route("/users/signout", methods=['POST'])
def signout():
    session.pop('username', None)
    flash("You have been signed out.")
    return redirect(url_for('index'))

# Run the application
if __name__ == "__main__":
    app.run(debug=True, port=5003)
