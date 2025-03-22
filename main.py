import sys
import logging
from PyQt5.QtWidgets import QApplication
from ui_widgets import MainWindow, SplashScreen
from PyQt5.QtCore import QTimer

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

if __name__ == "__main__":
    logging.info("Starting Weather App...")

    app = QApplication(sys.argv)

    # Create and show splash screen
    splash = SplashScreen()
    splash.show()

    # Set a timer to close the splash screen after 3 seconds and show the main window
    QTimer.singleShot(3000, lambda: (splash.close_splash(), MainWindow().show()))

    # Start the application's event loop
    sys.exit(app.exec_())
