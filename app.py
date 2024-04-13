from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/events')
def events():
    return render_template('events.html')

@app.route('/tickets')
def tickets():
    return render_template('tickets.html')

@app.route('/sitemap')
def sitemap():
    return render_template('sitemap.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/information')
def information():
    return render_template('information.html')

@app.route('/user')
def user():
    return render_template('user.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)
