               from flask import Flask , render_template
app = Flask(__name__,template_folder='templates')

@app.route('/')

def index():
    return render_template('index.html')

@app.route('/signUp')
def signup():
    return render_template('signUp.html')

@app.route('/signIn')
def signin():
    return render_template('signIn.html')

if __name__ == '__main__':
    app.run(debug=True)
