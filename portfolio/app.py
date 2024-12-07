from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import sys
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from openai import OpenAI
import json
from functools import wraps
import hashlib

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///portfolio.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Email configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('EMAIL_USER', 'emamimmubinkhan2006@gmail.com')
app.config['MAIL_PASSWORD'] = os.getenv('EMAIL_PASSWORD')  # Add your app password here
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('EMAIL_USER', 'emamimmubinkhan2006@gmail.com')

# Initialize extensions
mail = Mail(app)
db = SQLAlchemy(app)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Create necessary directories
uploads_dir = os.path.join(app.root_path, 'static', 'uploads')
logs_dir = os.path.join(app.root_path, 'logs')
for directory in [uploads_dir, logs_dir]:
    if not os.path.exists(directory):
        os.makedirs(directory)

# Configure logging
logging.basicConfig(level=logging.INFO)
file_handler = RotatingFileHandler('logs/portfolio.log', maxBytes=10240, backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s'
))
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)
app.logger.info('Portfolio startup')

# Admin authentication
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'your-secure-password-hash')  # Store the hash, not plain password

def check_admin_auth():
    auth = request.authorization
    if not auth:
        return False
    
    # Hash the provided password
    password_hash = hashlib.sha256(auth.password.encode()).hexdigest()
    return auth.username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not check_admin_auth():
            return Response(
                'Could not verify your access level for that URL.\n'
                'You have to login with proper credentials', 401,
                {'WWW-Authenticate': 'Basic realm="Login Required"'})
        return f(*args, **kwargs)
    return decorated

# Models
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes

# Routes
@app.route('/')
def home():
    try:
        return render_template('index.html')
    except Exception as e:
        app.logger.error(f'Error in home route: {str(e)}')
        return 'An error occurred', 500

@app.route('/about')
def about():
    try:
        return render_template('about.html')
    except Exception as e:
        app.logger.error(f'Error in about route: {str(e)}')
        return 'An error occurred', 500

@app.route('/projects')
def projects():
    try:
        return render_template('projects.html')
    except Exception as e:
        app.logger.error(f'Error in projects route: {str(e)}')
        return 'An error occurred', 500

@app.route('/contact')
def contact():
    try:
        return render_template('contact.html', active_page='contact')
    except Exception as e:
        app.logger.error(f'Error in contact route: {str(e)}')
        return 'An error occurred', 500

@app.route('/blog')
def blog():
    try:
        posts = BlogPost.query.order_by(BlogPost.created_at.desc()).all()
        return render_template('blog.html', posts=posts)
    except Exception as e:
        app.logger.error(f'Error in blog route: {str(e)}')
        return 'An error occurred', 500

@app.route('/blog/new', methods=['GET', 'POST'])
def new_post():
    try:
        if request.method == 'POST':
            title = request.form.get('title')
            content = request.form.get('content')
            
            if title and content:
                post = BlogPost(title=title, content=content)
                db.session.add(post)
                db.session.commit()
                flash('Blog post created successfully!', 'success')
                return redirect(url_for('blog'))
            
            flash('Title and content are required!', 'error')
        return render_template('new_post.html')
    except Exception as e:
        app.logger.error(f'Error in new_post route: {str(e)}')
        return 'An error occurred', 500

@app.route('/blog/<int:post_id>')
def view_post(post_id):
    try:
        post = BlogPost.query.get_or_404(post_id)
        return render_template('view_post.html', post=post)
    except Exception as e:
        app.logger.error(f'Error in view_post route: {str(e)}')
        return 'An error occurred', 500

@app.route('/blog/delete/<int:post_id>', methods=['POST'])
@admin_required
def delete_post(post_id):
    try:
        post = BlogPost.query.get_or_404(post_id)
        db.session.delete(post)
        db.session.commit()
        flash('Post deleted successfully!', 'success')
        return redirect(url_for('blog'))
    except Exception as e:
        app.logger.error(f'Error deleting post: {str(e)}')
        flash('Error deleting post!', 'error')
        return redirect(url_for('blog'))

@app.route('/chatbot')
def chatbot():
    messages = ChatMessage.query.order_by(ChatMessage.created_at.desc()).limit(10).all()
    messages.reverse()  # Show messages in chronological order
    return render_template('chatbot.html', messages=messages)

@app.route('/api/chat', methods=['POST'])
def chat_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
            
        user_message = data.get('message', '').strip()
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400

        # Create system message with context about your portfolio
        system_message = """You are an AI assistant for a portfolio website. You can help visitors learn about:
        - The website owner's skills and experience
        - Projects and work samples
        - Professional background and achievements
        - How to get in contact
        Be professional, friendly, and concise in your responses."""

        try:
            # Get response from OpenAI
            chat_completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )

            # Extract the bot's response
            bot_response = chat_completion.choices[0].message.content

            # Save the conversation to database
            chat_message = ChatMessage(user_message=user_message, bot_response=bot_response)
            db.session.add(chat_message)
            db.session.commit()

            return jsonify({
                'response': bot_response,
                'timestamp': datetime.utcnow().isoformat()
            })

        except Exception as api_error:
            app.logger.error(f'OpenAI API error: {str(api_error)}')
            return jsonify({'error': 'Error communicating with AI service'}), 500

    except Exception as e:
        app.logger.error(f'Error in chat API: {str(e)}')
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/clear_chat', methods=['POST'])
def clear_chat():
    try:
        # Delete all chat messages
        ChatMessage.query.delete()
        db.session.commit()
        return jsonify({'message': 'Chat history cleared successfully'})
    except Exception as e:
        app.logger.error(f'Error clearing chat: {str(e)}')
        return jsonify({'error': 'Failed to clear chat history'}), 500

@app.route('/notes')
def notes():
    try:
        notes_list = Note.query.order_by(Note.created_at.desc()).all()
        return render_template('notes.html', notes=notes_list)
    except Exception as e:
        app.logger.error(f'Error in notes route: {str(e)}')
        return 'An error occurred', 500

@app.route('/upload_note', methods=['POST'])
def upload_note():
    try:
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('notes'))
        
        file = request.files['file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('notes'))

        if file:
            # Check file type
            allowed_extensions = {'pdf', 'jpg', 'jpeg', 'png'}
            if not '.' in file.filename or \
               file.filename.rsplit('.', 1)[1].lower() not in allowed_extensions:
                flash('Invalid file type. Only PDF and images are allowed.', 'error')
                return redirect(url_for('notes'))

            # Secure filename and save file
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_')
            unique_filename = timestamp + filename
            file_path = os.path.join(uploads_dir, unique_filename)
            file.save(file_path)

            # Create note record
            note = Note(
                title=request.form.get('title', filename),
                filename=unique_filename,
                file_type=file.filename.rsplit('.', 1)[1].lower(),
                file_size=os.path.getsize(file_path)
            )
            db.session.add(note)
            db.session.commit()

            flash('File uploaded successfully!', 'success')
            return redirect(url_for('notes'))

    except Exception as e:
        app.logger.error(f'Error in upload_note route: {str(e)}')
        flash('An error occurred while uploading the file', 'error')
        return redirect(url_for('notes'))

@app.route('/download_note/<int:note_id>')
def download_note(note_id):
    try:
        note = Note.query.get_or_404(note_id)
        file_path = os.path.join(uploads_dir, note.filename)
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        app.logger.error(f'Error in download_note route: {str(e)}')
        flash('An error occurred while downloading the file', 'error')
        return redirect(url_for('notes'))

@app.route('/send_message', methods=['POST'])
def send_message():
    try:
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')

        if not all([name, email, subject, message]):
            flash('Please fill in all fields', 'error')
            return redirect(url_for('contact'))

        # Create email content
        email_body = f"""
        New message from your portfolio website:
        
        From: {name} <{email}>
        Subject: {subject}
        
        Message:
        {message}
        """

        msg = Message(
            subject=f"Portfolio Contact: {subject}",
            recipients=[app.config['MAIL_USERNAME']],
            body=email_body,
            reply_to=email
        )

        mail.send(msg)
        flash('Your message has been sent successfully!', 'success')
        return redirect(url_for('contact'))

    except Exception as e:
        app.logger.error(f'Error sending email: {str(e)}')
        flash('An error occurred while sending your message. Please try again.', 'error')
        return redirect(url_for('contact'))
import hashlib
new_password = "qweasd123"
hash = hashlib.sha256(new_password.encode()).hexdigest()
print(hash)
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
