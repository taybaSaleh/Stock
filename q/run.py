from app import create_app
from flask.cli import with_appcontext

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
