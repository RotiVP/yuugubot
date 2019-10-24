import flask
import ybapi

app = flask.Flask(__name__)

@app.route('/', methods=['POST'])
def index():
    body = flask.request.get_data().decode('utf-8')
    res = ybapi.handleReqbody(body)
    return res

if __name__ == "__main__":
    app.run(host='0.0.0.0', ssl_context='adhoc', port='5000')
