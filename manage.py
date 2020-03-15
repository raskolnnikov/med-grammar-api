import os
import unittest

from flask_script import Manager
from flask_script import Manager

from app import api_blueprint
from app import views_blueprint
from app.main import create_app

app = create_app(os.getenv('BOILERPLATE_ENV') or 'dev')
app.register_blueprint(api_blueprint, url_prefix='/api')
app.register_blueprint(views_blueprint, url_prefix='/web')

app.app_context().push()

manager = Manager(app)

@manager.command
def run():
    app.run(host='0.0.0.0', port=5000)


@manager.command
def test():
    """Runs the unit tests."""
    tests = unittest.TestLoader().discover('app/test', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

if __name__ == '__main__':
    manager.run()
