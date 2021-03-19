import flask
from flask_swagger_ui import get_swaggerui_blueprint

app = flask.Flask(__name__)
app.config['UPLOAD_EXTENSIONS'] = ['.jpg', '.png', '.gif', '.txt', '.pdf', '.csv']

SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "API fil rouge_v0.3"
    }
)
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)

from my_flask_package import routes
# delayed import necessary to avoid circular dependencies, since routes needs the app object
