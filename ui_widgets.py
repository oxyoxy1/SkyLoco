import logging
import pygame
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QLineEdit,
    QTabWidget, QMainWindow, QApplication, QScrollArea, QSplashScreen
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QFont, QIcon
from weather_api import (
    get_weather_data, get_forecast_data, get_location_data, save_weather_data,
    load_weather_data, get_weather_news, get_weather_icon
)
import datetime

class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SkyLoco - Loading...")
        self.setMinimumSize(600, 400)
        self.setWindowIcon(QIcon('icon.ico'))
        
        splash_layout = QVBoxLayout(self)
        
        splash_image = QLabel(self)
        pixmap = QPixmap("splash_image.png")  # Path to your splash image
        splash_image.setPixmap(pixmap)
        splash_layout.addWidget(splash_image)
        
        splash_text = QLabel("Loading SkyLoco...", self)
        splash_text.setFont(QFont("Arial", 20))
        splash_text.setAlignment(Qt.AlignCenter)
        splash_layout.addWidget(splash_text)
        
        self.setLayout(splash_layout)
        self.setWindowFlag(Qt.FramelessWindowHint)  # Remove window borders
        self.setAttribute(Qt.WA_TranslucentBackground)  # Optional, for transparency effect

    def close_splash(self):
        self.close()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SkyLoco - oxy")
        self.setMinimumSize(1280, 800)

        # Set the window icon
        self.setWindowIcon(QIcon('icon.ico'))

        logging.info("Initializing Main Window...")

        # Initialize pygame mixer for music
        pygame.mixer.init()

        # Start playing background music
        self.play_music()

        # Set up main content area
        self.tabs = QTabWidget(self)
        self.weather_tab = WeatherTab()
        self.location_tab = LocationTab(self)
        self.forecast_tab = ForecastTab()
        self.news_tab = NewsTab()

        self.tabs.addTab(self.weather_tab, "Current Weather")
        self.tabs.addTab(self.forecast_tab, "Week Forecast")
        self.tabs.addTab(self.location_tab, "Saved Locations")
        self.tabs.addTab(self.news_tab, "Weather News")

        sidebar = Sidebar()
        sidebar.current_weather_button.clicked.connect(self.show_weather_tab)
        sidebar.forecast_button.clicked.connect(self.show_forecast_tab)
        sidebar.location_button.clicked.connect(self.show_location_tab)
        sidebar.news_button.clicked.connect(self.show_news_tab)

        main_layout = QVBoxLayout()
        main_layout.addWidget(sidebar)
        main_layout.addWidget(self.tabs)

        central_widget = QWidget(self)
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def play_music(self):
        try:
            # Load and play background music (adjust the file path as needed)
            pygame.mixer.music.load("background_music.mp3")
            pygame.mixer.music.play(-1)  # Loop indefinitely
            logging.info("Background music started.")
        except pygame.error as e:
            logging.error(f"Error playing music: {e}")

    def show_weather_tab(self):
        logging.info("Switching to current weather...")
        self.tabs.setCurrentWidget(self.weather_tab)

    def show_forecast_tab(self):
        logging.info("Switching to weekly forecast...")
        self.tabs.setCurrentWidget(self.forecast_tab)

    def show_location_tab(self):
        logging.info("Switching to saved locations...")
        self.tabs.setCurrentWidget(self.location_tab)

    def show_news_tab(self):
        logging.info("Switching to news...")
        self.tabs.setCurrentWidget(self.news_tab)


class WeatherTab(QWidget):
    def __init__(self):
        super().__init__()
        logging.info("Initializing current weather...")
        self.layout = QVBoxLayout(self)
        
        self.weather_label = QLabel("Current Weather Information Here", self)
        self.layout.addWidget(self.weather_label)

        self.weather_icon_label = QLabel(self)  # Image label for the icon
        self.layout.addWidget(self.weather_icon_label)

        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Enter City Name or Full Zip Code (e.g., 92336-4116)")
        self.layout.addWidget(self.city_input)

        self.fetch_button = QPushButton("Get Weather", self)
        self.fetch_button.clicked.connect(self.fetch_weather)
        self.layout.addWidget(self.fetch_button)

        self.copy_button = QPushButton("Copy Text", self)
        self.copy_button.clicked.connect(self.copy_text)
        self.layout.addWidget(self.copy_button)

    def fetch_weather(self):
        city = self.city_input.text()
        logging.info(f"Fetching weather for city: {city}")
        self.fetch_weather_for_city(city)

    def fetch_weather_for_city(self, city):
        location = get_location_data(city)

        if location:
            latitude, longitude = location
            logging.info(f"Location found: Latitude {latitude}, Longitude {longitude}")
            weather_data = get_weather_data(latitude, longitude)

            if weather_data:
                logging.info(f"Weather data retrieved: {weather_data}")
                weather_info = (
                    f"Temperature: {weather_data['temperature']}°C / "
                    f"{(weather_data['temperature'] * 9/5) + 32:.1f}°F / "
                    f"{weather_data['temperature'] + 273.15:.1f}K\n"
                    f"Wind Speed: {weather_data['windspeed']} km/h / "
                    f"{weather_data['windspeed'] * 0.621371:.1f} mph\n"
                )
                humidity = weather_data.get('humidity', None)
                if humidity is not None and humidity != "N/A":
                    weather_info += f"Humidity: {humidity}%\n"

                self.weather_label.setText(weather_info)

                # Set the icon with resizing
                pixmap = QPixmap(weather_data['icon'])
                resized_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio)
                self.weather_icon_label.setPixmap(resized_pixmap)

                save_weather_data(city, weather_data)
            else:
                self.weather_label.setText("Error retrieving weather data.")
                logging.error(f"Failed to retrieve weather data for {city}")
        else:
            self.weather_label.setText("City not found in the system.")
            logging.error(f"City not found: {city}")

    def copy_text(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.weather_label.text())
        logging.info("Weather information copied to clipboard.")


class ForecastTab(QWidget):
    def __init__(self):
        super().__init__()
        logging.info("Initializing weekly forecast...")
        self.content_widget = QWidget(self)
        self.layout = QVBoxLayout(self.content_widget)

        self.forecast_label = QLabel("Weekly Forecast Information Here", self)
        self.layout.addWidget(self.forecast_label)

        self.forecast_day_layouts = []
        for i in range(7):  # Assuming 7-day forecast
            forecast_layout = QVBoxLayout()
            day_data_label = QLabel(self)
            icon_label = QLabel(self)
            forecast_layout.addWidget(day_data_label)
            forecast_layout.addWidget(icon_label)
            self.forecast_day_layouts.append((day_data_label, icon_label, forecast_layout))
            self.layout.addLayout(forecast_layout)

        self.city_input = QLineEdit(self)
        self.city_input.setPlaceholderText("Enter City Name or Full Zip Code")
        self.layout.addWidget(self.city_input)

        self.fetch_button = QPushButton("Get Forecast", self)
        self.fetch_button.clicked.connect(self.fetch_forecast)
        self.layout.addWidget(self.fetch_button)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidget(self.content_widget)
        self.scroll_area.setWidgetResizable(True)

        final_layout = QVBoxLayout(self)
        final_layout.addWidget(self.scroll_area)
        self.setLayout(final_layout)

    def fetch_forecast(self):
        city = self.city_input.text()
        logging.info(f"Fetching forecast for city: {city}")
        location = get_location_data(city)

        if location:
            latitude, longitude = location
            logging.info(f"Location found: Latitude {latitude}, Longitude {longitude}")
            forecast_data = get_forecast_data(latitude, longitude)

            if forecast_data:
                for day_data_label, icon_label, _ in self.forecast_day_layouts:
                    day_data_label.clear()
                    icon_label.clear()

                daily_data = forecast_data.get('daily', {})
                for i, date in enumerate(daily_data.get('time', [])):
                    day = datetime.datetime.strptime(date, '%Y-%m-%d').strftime('%A')
                    max_temp = daily_data.get('temperature_2m_max', [])[i]
                    min_temp = daily_data.get('temperature_2m_min', [])[i]
                    wind_speed = daily_data.get('windspeed_10m_max', [])[i]
                    precip = daily_data.get('precipitation_sum', [])[i]

                    forecast_info = (
                        f"Date: {day}, {date}\n"
                        f"Max Temp: {max_temp}°C / {(max_temp * 9/5) + 32:.1f}°F\n"
                        f"Min Temp: {min_temp}°C / {(min_temp * 9/5) + 32:.1f}°F\n"
                        f"Wind Speed: {wind_speed} km/h / {wind_speed * 0.621371:.1f} mph\n"
                        f"Precip: {precip} mm\n"
                    )
                    self.forecast_day_layouts[i][0].setText(forecast_info)
                    icon_filename = get_weather_icon(max_temp, wind_speed, precip)
                    icon_path = f"{icon_filename}"
                    pixmap = QPixmap(icon_path)
                    resized_pixmap = pixmap.scaled(32, 32, Qt.KeepAspectRatio)
                    self.forecast_day_layouts[i][1].setPixmap(resized_pixmap)

                logging.info("Forecast data successfully retrieved.")
            else:
                self.forecast_label.setText("Error retrieving forecast data.")
                logging.error("Failed to retrieve forecast data.")
        else:
            self.forecast_label.setText("City not found in the system.")
            logging.error(f"City not found: {city}")


class LocationTab(QWidget):
    def __init__(self, main_window):
        super().__init__()
        logging.info("Initializing saved locations...")
        self.main_window = main_window
        self.layout = QVBoxLayout(self)
        self.location_label = QLabel("List of Previous Locations", self)
        self.layout.addWidget(self.location_label)

        self.locations_list = QComboBox(self)
        self.layout.addWidget(self.locations_list)
        self.populate_location_list()

        self.locations_list.currentTextChanged.connect(self.location_changed)

    def populate_location_list(self):
        saved_data = load_weather_data()
        logging.info("Loading saved weather data...")
        for city in saved_data.keys():
            self.locations_list.addItem(city)
        logging.info(f"Locations populated: {list(saved_data.keys())}")

    def location_changed(self, city):
        logging.info(f"Location changed to {city}. Switching to current weather...")
        self.main_window.show_weather_tab()
        self.main_window.weather_tab.fetch_weather_for_city(city)


class NewsTab(QWidget):
    def __init__(self):
        super().__init__()
        logging.info("Initializing NewsTab...")
        self.layout = QVBoxLayout(self)
        self.news_label = QLabel("News Information Here", self)
        self.layout.addWidget(self.news_label)

        self.fetch_button = QPushButton("Get Weather News", self)
        self.fetch_button.clicked.connect(self.fetch_news)
        self.layout.addWidget(self.fetch_button)

    def fetch_news(self):
        news_data = get_weather_news()
        logging.info("Fetching weather news...")
        if news_data:
            news_info = "<html>"
            for article in news_data[:5]:
                news_info += (
                    f"<b>Title:</b> {article['title']}<br>"
                    f"<b>Description:</b> {article['description']}<br>"
                    f"<a href='{article['url']}'>Click here for more</a><br><br>"
                )
            news_info += "</html>"
            self.news_label.setText(news_info)
            self.news_label.setOpenExternalLinks(True)
            logging.info("Weather news successfully retrieved.")
        else:
            self.news_label.setText("Error fetching weather news.")
            logging.error("Failed to fetch weather news.")


class Sidebar(QWidget):
    def __init__(self):
        super().__init__()
        logging.info("Initializing Sidebar...")
        self.layout = QVBoxLayout(self)

        self.current_weather_button = QPushButton("Current Weather", self)
        self.forecast_button = QPushButton("Forecast", self)
        self.location_button = QPushButton("Locations", self)
        self.news_button = QPushButton("Weather News", self)

        self.layout.addWidget(self.current_weather_button)
        self.layout.addWidget(self.forecast_button)
        self.layout.addWidget(self.location_button)
        self.layout.addWidget(self.news_button)

        self.setLayout(self.layout)
        logging.info("Sidebar initialized.")


if __name__ == "__main__":
    app = QApplication([])

    # Create splash screen
    splash = SplashScreen()
    splash.show()

    # Timer to hide splash screen after 3 seconds and show main window
    QTimer.singleShot(3000, lambda: (splash.close_splash(), MainWindow().show()))

    logging.basicConfig(level=logging.INFO)

    # Start the application's event loop
    app.exec_()
