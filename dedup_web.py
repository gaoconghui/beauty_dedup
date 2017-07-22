from flask import Flask
from flask import request

from phash import ImageManager

app = Flask(__name__)

manager = ImageManager()


@app.route('/dedup')
def hello_world():
    key = request.args.get('key', '')
    if not key:
        return "False"
    return str(manager.has_same(manager.get_image(key)))


if __name__ == '__main__':
    app.run()
