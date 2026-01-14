from flask import Flask, render_template, request, redirect, url_for, flash
import utils
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Change this in production

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['GET', 'POST'])
def analyze():
    if request.method == 'POST':
        repo_url = request.form.get('repo_url')
        if not repo_url:
            flash('Please enter a GitHub URL', 'error')
            return redirect(url_for('analyze'))
        
        data = utils.analyze_repo(repo_url)
        if "error" in data:
            flash(data['error'], 'error')
            return redirect(url_for('analyze'))
            
        return render_template('analyze.html', data=data)
    
    return render_template('analyze.html', data=None)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            flash('Please enter a search term', 'error')
            return redirect(url_for('search'))
            
        results = utils.search_repos(query)
        return render_template('search.html', results=results, query=query)
        
    return render_template('search.html', results=None)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        username = request.form.get('username')
        if not username:
            flash('Please enter a username', 'error')
            return redirect(url_for('profile'))
            
        data = utils.analyze_user(username)
        if "error" in data:
            flash(data['error'], 'error')
            return redirect(url_for('profile'))
            
        return render_template('profile.html', data=data)
        
    return render_template('profile.html', data=None)

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/register')
def register():
    return render_template('register.html')

#if __name__ == '__main__':
 #   app.run(debug=True)
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=False)