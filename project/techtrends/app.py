import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort

# in order to be able to use logging, the module has to be imported
import logging
import sys

# To count all database connection, we need a variable
connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    # for each connection to the database, 
    # increment the connection counter
    connection_count = connection_count + 1
    return connection



# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post



# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'


# Students wil be able to apply the best practices to develop an application
# I found a hint at the knowledge base 
# https://knowledge.udacity.com/questions/612353
# get the standard logger
logger = logging.getLogger("__name__")
# Here i define the logging level DEBUG
# writing the logs to a logfile and
# setting the message's format to 
# - timestamp: %(asctime)s
# - loglevel: %(levelname)s
# - logger's name: %(name)s
# - thread name: %(threadName)s
# - log message: %(message)s 
logging.basicConfig(filename="app.log", level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s')
# create a handler for STDOUT
out_handler = logging.StreamHandler(sys.stdout)
out_handler.setLevel(logging.DEBUG)
# create a handler for STDERR
err_handler = logging.StreamHandler(sys.stderr)
err_handler.setLevel(logging.ERROR)
# add the handler to the logger
logger.addHandler(out_handler)
#logger.addHandler(err_handler)


# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)



# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
      # logging: 404 page when a non existing article is accessed
      app.logger.error("Article {id} does not exist".format(id=post_id))  
      return render_template('404.html'), 404
    else:
      # logging: access an article  
      app.logger.info("Article '{title}' delivered".format(title=post['title']))  
      return render_template('post.html', post=post)



# Define the About Us page
@app.route('/about')
def about():
    # logging: access about us page
    app.logger.info("About page delivered")  
    return render_template('about.html')



# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            # logging: a new article is created
            app.logger.info("Article '{title}' created".format(title=title))  
            return redirect(url_for('index'))

    return render_template('create.html')



# Students wil be able to apply the best practices to develop an application
# Here I define the "/healthz" endpoint
# This is basically the source code we learned from the lesson
@app.route('/healthz')
def healthz():
    response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
    )
    return response



# In order not to destroy/overwrite the original requirement
# I decided to put the dynamic healthcheck in a separate function
# it is basically the same code but includes a test if the database is available
# if so, a 200 response is returned
# if the database is not accessible, a 500 response is returned 
@app.route('/health_dyn')
def healthz_dyn():
    try:
        connection = get_db_connection()
        connection.cursor()
        connection.execute('SELECT * FROM posts')
        connection.close()
        response = app.response_class(
            response=json.dumps({"result":"OK - healthy"}),
            status=200,
            mimetype='application/json'
        )
        return response
    except Exception:
        response = app.response_class(
            response=json.dumps({"result":"ERROR - not healthy"}),
            status=500,
            mimetype='application/json'
        )
        return response



# Students wil be able to apply the best practices to develop an application
# Here I define the "/metrics" endpoint
# This is basically the source code we learned from the lesson 
@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    post_count = len(posts)
    response = app.response_class(
        response=json.dumps({"db_connection_count": connection_count, "post_count": post_count}),
        status=200,
        mimetype='application/json'
    )
    return response



# start the application on port 3111
if __name__ == "__main__":
   app.run(host='0.0.0.0', port='3111')
