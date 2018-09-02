import os
from app import create_app, db
from app.models import User, Entry
from flask_migrate import Migrate

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
migrate = Migrate(app, db)
