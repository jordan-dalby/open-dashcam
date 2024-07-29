from logging.handlers import RotatingFileHandler
from presenter import DashCamPresenter
from model import DashCamModel
from view import DashCamView
import logging

def setup_logging():
    log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    log_file = 'dashcam.log'
    log_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=5)
    log_handler.setFormatter(log_formatter)
    log_handler.setLevel(logging.DEBUG)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    console_handler.setLevel(logging.DEBUG)

    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_handler)
    logger.addHandler(console_handler)

    return logger

if __name__ == '__main__':
    logger = setup_logging()
    logger.debug("Logging initialized")

    try:
        model = DashCamModel()
        print(model.get_camera_info())
        
        presenter = DashCamPresenter(model, logger)
        view = DashCamView(presenter)

        logger.info("Starting Flask application")
        view.run(host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error initializing DashCamModel: {str(e)}")