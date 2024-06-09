from kivy_garden.mapview import MapView, MapMarker
from kivy.network.urlrequest import UrlRequest
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.button import Button
from kivy_garden.graph import Graph, MeshLinePlot
from kivy.lang import Builder
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.checkbox import CheckBox
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.core.window import Window
from kivy.uix.dropdown import DropDown
from kivy.uix.image import Image
from kivy.uix.spinner import Spinner
from kivy.graphics import *
from kivy.core.window import Window

import requests
import os
import csv

Builder.load_file('design.kv')

class StartScreen(Screen):

    # Initialize the start screen
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        pass

class ResearchScreen(Screen):

    # Initializing lat, long, and zoom
    lat = long = zoom = 19
    lat = 35.770849
    long = -78.674706

    # File path
    file_path = 'C:\\Users\\malin\\Documents\\GitHub\\wolfwagen\\Server\\logged_data.csv'

    # Initialize the start screen
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize the mapview
        self.mapview = MapView(zoom = self.zoom, lat = self.lat, lon = self.long)

        # Creating a plot for tracking the data
        self.graphview = Graph(xlabel='X', ylabel='Y', x_ticks_minor=5, x_ticks_major=25, y_ticks_minor=1,
                      y_ticks_major=10, y_grid_label=True, x_grid_label=True, padding=5,
                      xlog=False, ylog=False, xmin=-0, xmax=100, ymin=-1, ymax=1)
        plot = MeshLinePlot(color=[1, 0, 0, 1])
        plot.points = [(x, 0.5 * x * 0.01) for x in range(0, 101)]
        self.graphview.add_plot(plot)

        # Add the map to the widget
        map = self.ids.research_widget
        map.add_widget(self.mapview)

        # Initialize each of the check boxes initialized
        self.rtk_check = self.ids.rtk_cb.active
        self.gps_check = self.ids.gps_cb.active
        self.ml_check = self.ids.ml_cb.active

        # Initialize the lists for each 1D list of data
        self.rtk_data = []
        self.gps_data = []
        self.ml_data = []
        self.times = []

        # Initialize the lists for each 1D list of statistics
        # Percent error
        self.gps_pe = []
        self.ml_pe = []

        # Create the research widget that holds either the plot or the map
        self.research_widget = self.ids.research_widget

        # Set the initial switch to 0
        self.widget_switch_state = 0
        self.log_switch_state = 0
        self.route_switch_state = 0

        # Constant loop of every 1 second
        Clock.schedule_interval(self.main_loop, 1)

    # Main loop that is repeats every second
    def main_loop(self, instance):

        # Receive the current data from the web server
        self.receive_data()

        self.calculate_stats()

        # Log data if it is turned on
        if self.log_switch_state == 1:
            self.log_data()
        
        # Constantly update the route on the map if needed
        if self.route_switch_state == 1:
            self.generate_route()

    # Calculate the statistics of the data
    def calculate_stats(self):

        # Calculate the percent difference between the points
        if len(self.gps_data) > 0 and len(self.ml_data) > 0 and len(self.rtk_data) > 0:
            self.gps_pe[len(self.gps_pe)] = self.percent_error(self.rtk_data[len(self.rtk_data) - 1], self.gps_data[len(self.gps_data) - 1])
            self.ml_pe[len(self.ml_pe)] = self.percent_error(self.rtk_data[len(self.rtk_data) - 1], self.ml_data[len(self.ml_data) - 1])

    # Calculates the percent error between expected and measured values
    def percent_error(self, expected, measured):
        pe = abs(float(expected - measured)) / float(measured)
        return pe

    # Logs the data to a csv
    def log_data(self):

        # Combine all the data into a 2D array
        data = [self.times, self.rtk_data, self.gps_data, self.ml_data, self.gps_pe, self.ml_data]

        # Writes the data to the csv of the file path and overwrites it if it already exists
        with open(self.file_path, 'w', newline='') as csv_file:
            writer = csv.writer(csv_file)
            writer.writerows(data)
    

    # Receives data from the server to then be logged to a csv and displayed
    def receive_data(self):

        # URL of the AWS server being used
        url = 'http://3.16.149.178/download/data.csv'

        # Get the response from the url
        response = requests.get(url)

        # Decode the byte string
        csv_content = response.content.decode('utf-8')

        # Split the content by lines
        lines = csv_content.splitlines()

        # Parse the csv to get the times and data 
        data = [line.split(',') for line in lines]
        if len(data) > 3:
            self.times[len(self.times)] = data[0].pop()
            self.rtk_data[len(self.rtk_data)] = data[1].pop()
            self.gps_data[len(self.gps_data)] = data[2].pop()
            self.ml_data[len(self.ml_data)] = data[3].pop()
        
    # When a checkbox is clicked, the data is updated to reflect which checkboxes are currently active
    def checkbox_clicked(self, instance, value):
        self.rtk_check = self.ids.rtk_cb.active
        self.gps_check = self.ids.gps_cb.active
        self.ml_check = self.ids.ml_cb.active

    # Finds the current route that it is on, and finds the next one
    # Checks that when it leaves a route, a new one is added
    # Two routes shown at a time, current and next
    def generate_route(self):
        pass
        
    # Allows the user to switch between views of the current tracked positions 
    # and the statistics between each position tracked (Percent error)
    def switch_widgets(self):
        
        # Get the current widget being displayed
        widget = self.research_widget.children[0]

        # Remove that current widget
        self.research_widget.remove_widget(widget)

        # If the switch state is 0, change it to 1 then display the graph
        # Else change it to 1 then display the map
        if self.widget_switch_state == 0:
            self.widget_switch_state += 1
            self.ids.switch_widget.text = 'Display Map'
            self.research_widget.add_widget(self.graphview)
        else:
            self.widget_switch_state -= 1
            self.ids.switch_widget.text = 'Display Statistics'
            self.research_widget.add_widget(self.mapview)

    # Logs the data of the GPS signals received via communication with ESP
    def switch_log(self):

        # If the log switch state is 1, the data will be logged consistently to a local csv file
        # Else the logging of the data is stopped
        if self.log_switch_state == 0:
            self.log_switch_state += 1
            self.ids.switch_log.text = 'End Logging'
            self.rtk_data = []
            self.gps_data = []
            self.ml_data = []
            self.times = []
            self.gps_pe = []
            self.ml_pe = []

            # Num initialize
            num = 1

            # Continue until a new file path is created
            while os.path.exists(self.file_path):
                self.file_path = self.file_path + str(num)
                num += 1
        else:
            self.log_switch_state -= 1
            self.ids.switch_log.text = 'Begin Logging'

    # Generate a constant set of waypoints for the car to travel and be displayed on the map
    def switch_route(self):

        # If the route switch is 1, it will begin to generate a random route for the 
        if self.route_switch_state == 0:
            self.route_switch_state += 1
            self.ids.switch_route.text = 'End Route Generation'
        else:
            self.route_switch_state -= 1
            self.ids.switch_route.text = 'Begin Route Generation'

class PrototypeScreen(Screen):

    # Initializing lat, long, and zoom
    lat = long = zoom = 19
    lat = 35.770849
    long = -78.674706

    # Initialize the start screen
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # Initialize the mapview
        self.mapview = MapView(zoom = self.zoom, lat = self.lat, lon = self.long)
        map = self.ids.map_widget
        map.add_widget(self.mapview)

        # Get the current position of each inactive vehicle
        points = self.get_vehicle_positions()

    def get_vehicle_positions(self):
        

class WW_MonitoringApp(App):

    def build(self):
        Window.fullscreen = 'auto'
        sm = ScreenManager()
        Window.clearcolor = (230/255, 230/255, 230/255, 1)
        sm.add_widget(StartScreen(name='start_screen'))
        sm.add_widget(ResearchScreen(name='research_screen'))
        sm.add_widget(PrototypeScreen(name='prototype_screen'))

        return sm

if __name__ == '__main__':
    WW_MonitoringApp().run()
