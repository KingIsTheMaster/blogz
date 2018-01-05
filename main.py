from flask import Flask, request, redirect, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc


app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:honeybun@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)


class Post(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(250))

    def __init__(self, title,body):
        self.title = title
        self.body = body

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