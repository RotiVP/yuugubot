from flask import Flask, request
#import os

import ybapi

#sk = os.urandom(24)

app = Flask(__name__)
#app.secret_key = sk

@app.route('/', methods=['POST'])
def index():
    body = request.get_data().decode('utf-8')
    res = ybapi.handleReqbody(body)
    return res

#@app.before_request
#def force_secure():
#    if request.url.startswith('http://'):
#        return redirect(request.url.replace('http://', 'https://'), code=301)

if __name__ == "__main__":
    app.run(host='0.0.0.0', ssl_context='adhoc', port='5000')
