from app import app, db
from app.models import User, Image, Roi


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Image': Image, 'Roi': Roi}


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
