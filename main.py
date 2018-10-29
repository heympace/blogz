from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:build-a-blog-pass@localhost:8889/build-a-blog'
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

@app.route('/blog', methods=['POST', 'GET'])
def index():

    if request.method == 'POST':
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        archived = False
        new_post = Blog(post_title, post_body, archived)
        db.session.add(new_post)
        db.session.commit()


    posts = Blog.query.filter_by(archived=False).all()
    # archived = Blog.query.filter_by(completed=True).all()
    
    return render_template('blog.html',title="My Blog", 
        posts=posts)

if __name__ == '__main__':
    app.run()