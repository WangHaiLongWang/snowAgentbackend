from flask import render_template, request, current_app
from app.main import bp
from app.models import Post

@bp.route('/')
@bp.route('/index')
def index():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page=page, per_page=current_app.config['POSTS_PER_PAGE'])
    return render_template('index.html', posts=posts)