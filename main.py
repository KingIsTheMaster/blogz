from flask import Flask, request, redirect, render_template, session, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bearclaw@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'gm0k38yOnbC3r2Co'

class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner_id):
        self.title = title
        self.body = body
        self.owner_id = owner_id

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(50))
    blog = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index', 'blog']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect(url_for('login'))

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = "Inlavid Username or Password"
        user = User.query.filter_by(username=username).first()

        if user:
            
            if user.password == password:
                session['username'] = username
                flash('Logged in!')
                return redirect ('/addpost')
            else:
                flash('Invalid Password', 'error')
        else: 

            flash('Username Nonexistent', 'error')

    return render_template('login.html')

@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        
        existing_user = User.query.filter_by(username=username).first()
        
        error = 'Username is taken'
        username_error = ''
        password_error = ''
        verify_error = ''

        if len(username) < 3 or len(username) > 30 or ' ' in username:
            username_error = 'Not a valid username'
            
        if len(password) < 3 or len(password) > 30 or ' ' in password:
            password_error = 'Not a valid password'

        if verify != password:
            verify_error = 'Passwords do not match'

        if username_error or password_error or verify_error:
                return render_template('signup.html', username_error=username_error, password_error=password_error, verify_error=verify_error)

        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/addpost')
        else:
            return render_template('signup.html', error=error)

    return render_template('signup.html')

@app.route('/logout')
def logout():
    del session['username']
    flash('Logged Out!')
    return redirect('/')


@app.route('/blog', methods=['POST','GET'])
def individual_post():
    
    post_id = request.args.get('id')
    post_user = request.args.get ('user')
    print(post_user)
    user_filt = User.query.filter_by(username=post_user).first()
    if post_id: 
        indv_post = Post.query.get(post_id)
        return render_template('individualpost.html', indv_post=indv_post)
    if user_filt:
        user_posts = Post.query.filter_by(owner_id=user_filt.id).all()
        return render_template('singleUser.html', user_posts=user_posts)
    else:
        post = Post.query.all()
        return render_template('blog.html', post=post)



@app.route('/addpost', methods=['POST','GET'])
def add_post():
    owner = User.query.filter_by(username=session['username']).first()
    error1 = ""
    error2 = ""
    
    if request.method == 'POST':
        post_title = request.form['title']
        post_body = request.form['body']
        
        if len(post_title) < 1:
            error1 = "This feild requires text!"
        elif len(post_body) < 1:
            error2 = "This feild requires text!"

        if not error1 and not error2: 
            new_post = Post(post_title, post_body, owner.id)
            db.session.add(new_post)
            db.session.commit()             
    
            return redirect('/blog?id=%s' % new_post.id)
            
        else: 
            return render_template('addpost.html', title="Blogz", error1 = error1, error2 = error2, post_title = post_title , post_body = post_body) 
   
    return render_template('addpost.html', title="Blogz", error1 = error1, error2 = error2)


@app.route('/', methods=['POST', 'GET'])
def index():
   
    user = User.query.all()
    return render_template('home.html', title="Blogz", user=user)


if __name__ == '__main__':
    app.run()