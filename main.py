from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:bearclaw@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title,body):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(50))
    blog = db.relationship('Post', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            return redirect('/')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']

        # TODO - validate user's data

        existing_user = User.query.filter_by(email=email).first()
        if not existing_user:
            new_user = User(email, password)
            db.session.add(new_user)
            db.session.commit()
            session['email'] = email
            return redirect('/')
        else:
            # TODO - user better response messaging
            return "<h1>Duplicate user</h1>"

    return render_template('register.html')

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/')


@app.route('/blog', methods=['POST','GET'])
def individual_post():
    
    post_id = request.args.get('id')
    indv_post = Post.query.get(post_id)
    return render_template('blog.html', indv_post=indv_post)



@app.route('/addpost', methods=['POST','GET'])
def add_post():
    
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
            new_post = Post(post_title, post_body)
            db.session.add(new_post)
            db.session.commit()             
    
            return redirect('/blog?id=%s' % new_post.id)
            
        else: 
            return render_template('addpost.html', title="Build a Blog", error1 = error1, error2 = error2, post_title = post_title , post_body = post_body) 
   
    return render_template('addpost.html', title="Build a Blog", error1 = error1, error2 = error2)


@app.route('/', methods=['POST', 'GET'])
def index():
   
    post = Post.query.all()
    return render_template('blogpost.html',title="Build a Blog", 
        post = post)


if __name__ == '__main__':
    app.run()