# Indoor climate assistant
Indoor climate assistant that can warn you when the temperature is too low or too high and when the air quality is too low. The assistant also provides extensive visualization of data related to the indoor climate.

## Design
The project is split into two parts, the desktop application and the sensor implementation. Retrieving data from the sensor, which is connected to a Raspberry Pi, is supported by the **pi_zero.py** file. Running this file from the Raspberry Pi that is connected to the BME680 sensor starts an infinite loop that continuously inserts data from the sensor into the PostgreSQL database. The BME680 sensor itself is configured and implemented in the **sensor.py** file, which serves as the interface between the sensor hardware and the program. Insertion of data into the PostgreSQL database is supported by the **database.py** file which also contains support for querying data from the database.

The desktop application is designed using an object-oriented approach where program execution starts from the **main_gui.py** file. The UI itself is implemented in the **mainwindow.ui** file, while functionality related to the elements shown on the main window is implemented in the **main_window.py** file. This file defines how the central graph, which is a matplotlib graph, is drawn according to the chosen settings and how the graph is updated with live data. To use a matplotlib graph in a QT UI, it is necessary to define a custom widget which supports matplotlib, which is done in the **mplwidget.py** file. Since the application is designed to run in the background, a system tray icon is used to visualize that the program is running and to ease the process of opening the application again. The icon itself and the actions that are available when left/right clicking the icon are implemented in the **system_tray.py** file.

## Graphical user interface
The user interface was created using the QT framework. An example of the user interface can be seen below.

![Example of GUI](https://i.imgur.com/XaWXRCy.png)

The "Data" combo box lets the user decide what data they want to see in the central graph. Here you can choose between "Air quality", "Temperature", "Air pressure", "Gas resistance" and "Humidity". The "Time frame" combo box is used to decide how much data is shown. "Now" shows the data from the last hour. "Today", "This week", "This month", "This year" and "All time" are the other options. 

The warnings can be toggled on and off using the checkboxes on the bottom right. If toggled on, a windows notification is sent to the user if the data exceeds the chosen thresholds. The thresholds for the warnings can be changed using the spin boxes.
