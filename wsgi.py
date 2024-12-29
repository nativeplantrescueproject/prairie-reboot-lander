from preboot_lander.config import ProductionConfig
from preboot_lander.app import create_app

# Instantiate log here, as the hosts API is requested to communicate with influx
app = create_app(config_class=ProductionConfig)

if __name__ == '__main__':
    app.run(host=ProductionConfig.DB_SERVER, port=ProductionConfig.PORT)
