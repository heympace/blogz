from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:passmeblogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

# used for security
app.secret_key = 'asdfasdfasdf;'

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(1200))
    pub_date = db.Column(db.DateTime)
    archived = db.Column(db.Boolean)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, archived, owner, pub_date=None):
        self.title = title
        self.body = body
        self.archived = False
        self.owner = owner
        if pub_date is None:
            pub_date = datetime.utcnow()
        self.pub_date = pub_date

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

# always runs first
# check for existance of user email in session directory
@app.before_request
def require_login():

    # need to whitelist pages user can see
    allowed_routes = ['login', 'list_users', 'list_blog', 'index', 'signup']

    # if endpoint isn't in allowed routes and no email...
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

# check for content to validate
def empty_string(response):
    if response == "":
        return True

# check for 3+ characters
def under_three_chars(response):
    if len(response) < 3:
        return True


#########################
###     index
#########################

@app.route('/', methods=['POST', 'GET'])
def list_users():
    users = User.query.all()
    return render_template('index.html', users=users)
    # get first, assign to variable, 
    # user_id = request.args.get('id') 
    # members = User.query.filter_by(username=username).all()

    #if user_id is None:
    #    users = User.query.filter_by(id=id).all()

        # archived = Blog.query.filter_by(completed=True).all()
    
    #    return render_template('index.html',title="User List", 
    #        users=users)
    #else:
    #    user = Blog.query.get(user_id)
    #    return render_template('post.html', 
    #        post_id=post_id, 
    #        post_title=post.title, 
    #        post_body=post.body
    #    )


#########################
###     LOGIN
#########################

@app.route('/login', methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        #verify email, get info from db to compare:
        user = User.query.filter_by(username=username).first()

        # if no user, user = None
        # if user does exist, compare password
        if user and user.password == password:

            # remember that the user is logged in
            session['username'] = username
            flash("Logged in")
            return redirect ('/newpost')

        elif user and not user.password == password:
            flash("User password incorrect, please try again", "error")
        elif not user:
            flash("Username does not exist, please try again", "error")

    return render_template('login.html')


#########################
###     SIGNUP
#########################

@app.route('/signup', methods=['POST', 'GET'])
def signup():

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['password_verify']

        # test for existing user
        existing_user = User.query.filter_by(username=username).first()

        if existing_user:
            flash("Username already exists, please enter a new username", "error")
            return render_template('signup.html')

        if empty_string(username):
            flash("Please enter a username", "error")
            return render_template('signup.html')

        if under_three_chars(username):
            flash("Username must be 3 or more characters", "error")
            return render_template('signup.html')

        if empty_string(password):
            flash("Please enter a password", "error")
            return render_template('signup.html', username=username)

        if under_three_chars(password):
            flash("Password must be 3 or more characters", "error")
            return render_template('signup.html')

        if password != verify:
            flash("Passwords don't match, please enter password", "error")
            return render_template('signup.html', username=username)

        if not existing_user:
            # add new user to db
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()

            # remember that the user is logged in
            session['username'] = username

            return redirect ('/newpost')
        
        else:
            # TODO - user better response message
            return "<h1>Please try a different username.</h1>"

    return render_template('signup.html')


#########################
###     BLOG
#########################

@app.route('/blog', methods=['POST', 'GET'])
def list_blogs():
    # get first, assign to variable, 
    post_id = request.args.get('id') 
    owner = User.query.filter_by(username=session['username']).first()

    if post_id is None:
        posts = Blog.query.filter_by(archived=False, owner=owner).all()
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

#########################
###     NEW POST
#########################

@app.route('/newpost', methods=['POST', 'GET'])
def addPost():

    owner = User.query.filter_by(username=session['username']).first()

    if request.method == 'POST':
        post_title = request.form['post_title']
        post_body = request.form['post_body']
        archived = False

        # error placeholders
        error_post_title = ''
        error_post_body = ''

        if empty_string(post_title):
            flash("Please enter a post title", "error")
            return render_template('newpost.html', post_body=post_body)

        if empty_string(post_body):
            flash("Please add post body content", "error")
            return render_template('newpost.html', post_title=post_title)

        if not error_post_title and not error_post_body:
            new_post = Blog(post_title, post_body, archived, owner)

            db.session.add(new_post)
            db.session.commit()

            posts = Blog.query.filter_by(archived=False).all()
            return redirect('/blog?id={0}'.format(new_post.id))

        else:
            return render_template('/newpost.html',
                post_title=post_title,
                post_body=post_body,
                )

    posts = Blog.query.filter_by(archived=False).all()
    # archived = Blog.query.filter_by(completed=True).all()
    
    return render_template('newpost.html',title="My Blog", 
        posts=posts)

#########################
###     LOGOUT
#########################

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

if __name__ == '__main__':
    app.run()