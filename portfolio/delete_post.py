from app import app, db, BlogPost

with app.app_context():
    post = BlogPost.query.filter_by(title='hi').first()
    if post:
        db.session.delete(post)
        db.session.commit()
        print("Post deleted successfully!")
    else:
        print("Post not found!")
