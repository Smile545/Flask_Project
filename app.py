from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SECRET_KEY'] = 'admin'
db = SQLAlchemy(app)
app.app_context().push()

admin = Admin(app)

class Category(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(20), nullable = False, unique = True)
    articles = db.relationship('Article', backref = 'category_name')
    
    def __repr__(self):
        return f'Category: {self.id} - {self.name}'
    

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    title = db.Column(db.String(50), nullable=False, unique = True)
    introduction = db.Column(db.String(100), nullable = False)
    text = db.Column(db.Text(), nullable = False)
    pub_date = db.Column(db.DateTime, default = datetime.utcnow)
    
    def __repr__(self):
        return f'Article: {self.id} - {self.title}'


admin.add_view(ModelView(Category, db.session))
admin.add_view(ModelView(Article, db.session))


@app.route('/')
def index():
    latest_articles = Article.query.order_by(Article.pub_date.desc())[:2]
    latest_articles2 = Article.query.order_by(Article.pub_date.desc())[2:5]
    
    return render_template('index.html', articles = latest_articles, articles2 = latest_articles2 )



@app.route('/new_post', methods = ['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        category_id = request.form['category_select']
        title = request.form['title']
        introduction = request.form['introduction']
        text = request.form['article_text']
        
        article = Article(category_id = category_id, 
                          title = title,
                          introduction = introduction,
                          text = text)
        try:
            db.session.add(article)
            db.session.commit()
            
            return redirect(url_for('index'))
        except Exception as error:
            return f'Возникла ошибка -> {error}'
    else:
        categories = Category.query.all()
        
        return render_template('new_post.html', categories = categories)

@app.route('/detailed_post/<int:article_id>')
def detailed_post(article_id):
    article = Article.query.get_or_404(article_id)
    return render_template('detailed.html', article = article)


if __name__ == '__main__':
    app.run(debug=True)