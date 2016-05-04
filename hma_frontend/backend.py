from flask import Flask, make_response

app = Flask(__name__)

@app.route("/hello")
def hello():
    return "<h1 style='color:blue'>Hello There!</h1>"

@app.route('/')
def index():
    """
    send_file() means that the files will be cached, we use make_response()
    instead for development
    """
    #return app.send_static_file('index.html')
    #return make_response(open('templates/index.html').read())
    return make_response(open('templates/searchResults.html').read())

@app.route('/protoview')
def protoview():
    return make_response(open('templates/protoview.html').read())

@app.route('/view4')
def view4():
    return make_response(open('templates/view4.html').read())

@app.route('/view3')
def view3():
    return make_response(open('templates/view3.html').read())

@app.route('/searchResults')
def searchResults():
    return make_response(open('templates/searchResults.html').read())

@app.route('/<path:path>')
def static_proxy(path):
  # send_static_file will guess the correct MIME type
  return app.send_static_file(path)

if __name__ == "__main__":
    #app.run(host='0.0.0.0')
    app.run()
