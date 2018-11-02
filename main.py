from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:passmeblogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    archived = db.Column(db.Boolean)

    def __init__(self, title, body, archived):
        self.title = title
        self.body = body
        self.archived = False

# check for content to validate
def empty_string(response):
    if response == "":
        return True

@app.route('/blog', methods=['POST', 'GET'])
def index():
    # get first, assign to variable, 
    post_id = request.args.get('id') # connects from redirect in line 72

    if post_id is None:
        posts = Blog.query.filter_by(archived=False).all()
        # archived = Blog.query.filter_by(completed=True).all()
    
        return render_template('blog.html',title="My Blog", 
            posts=posts)
    else:
        post = Blog.query.get(post_id)
        return render_template('post.html', 
            post_id=post_id, 
            post_title=post.title, 
            post_body=post.body
        )


@app.route('/newpost', methods=['POST', 'GET'])
def addPost():

    if request.method == 'POST':
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        archived = False

        # error placeholders
        error_post_title = ''
        error_post_body = ''

        if empty_string(post_title):
            error_post_title = 'Title required'

        if empty_string(post_body):
            error_post_body = 'Content required'

        if not error_post_title and not error_post_body:
            new_post = Blog(post_title, post_body, archived)

            db.session.add(new_post)
            db.session.commit()

            posts = Blog.query.filter_by(archived=False).all()
            return redirect('/blog?id={0}'.format(new_post.id))

        else:
            return render_template('/newpost.html',
                post_title=post_title,
                post_body=post_body,
                error_post_title=error_post_title,
                error_post_body=error_post_body)

    posts = Blog.query.filter_by(archived=False).all()
    # archived = Blog.query.filter_by(completed=True).all()
    
    return render_template('newpost.html',title="My Blog", 
        posts=posts)

if __name__ == '__main__':
    app.run()