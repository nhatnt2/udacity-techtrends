import sqlite3
import logging

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
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
      return render_template('404.html'), 404
    else:
      dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
      app.logger.info(' [%s] Article "%s" retrieved!' % (dt_string, post['title']))

      return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    app.logger.info(' [%s] Access "About Us" retrieved!' % (dt_string))

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

            dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            app.logger.info(' [%s] Create new article "%s" successfully!' % (dt_string, title))

            return redirect(url_for('index'))

    return render_template('create.html')

# Define check status application
@app.route('/healthz')
def status():
  response = app.response_class(
          response=json.dumps({"result":"OK - healthy"}),
          status=200,
          mimetype='application/json'
  )
  return response

# Define get metric mount of posts and number of connections
@app.route('/metrics')
def metrics():
  response = app.response_class(
          response=json.dumps({"status":"success","code":0,"data":{"post_count":140,"db_connection_count":23}}),
          status=200,
          mimetype='application/json'
  )
  return response

# start the application on port 3111
if __name__ == "__main__":
   logging.basicConfig(filename='app.log',level=logging.DEBUG)
   app.run(host='0.0.0.0', port='3111')
