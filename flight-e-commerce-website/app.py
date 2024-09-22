from flask import Flask
from authentication_routes import authentication_routes
from chuyen_bay_routes import chuyen_bay_routes
from dat_ve_routes import dat_ve_routes
from ban_ve_routes import ban_ve_routes
from lich_chuyen_bay_routes import lich_chuyen_bay_routes
from ve_chuyen_bay_routes import ve_chuyen_bay_routes
from quy_dinh_routes import quy_dinh_routes

app = Flask(__name__)
app.secret_key = 'your_secret_key'



# Register the authentication routes Blueprint
app.register_blueprint(authentication_routes, url_prefix='/')

app.register_blueprint(chuyen_bay_routes, url_prefix='/')
app.register_blueprint(dat_ve_routes, url_prefix='/')
app.register_blueprint(ban_ve_routes, url_prefix='/')
app.register_blueprint(lich_chuyen_bay_routes, url_prefix='/')
app.register_blueprint(ve_chuyen_bay_routes, url_prefix='/')
app.register_blueprint(quy_dinh_routes, url_prefix='/')

if __name__ == '__main__':
    app.run(debug=True)
