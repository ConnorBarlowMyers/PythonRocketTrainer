import sys
import random
import numpy as np
import math

from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QTimer, QEventLoop
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QMainWindow, QToolBar, QPushButton, QHBoxLayout, QFileDialog
from PyQt5.QtWidgets import QGridLayout, QLineEdit, QApplication, QLabel

from training_generation import PlanManager
from pynput.keyboard import Key, Controller


keyboard = Controller()


# a pyqt friendly version of time.sleep - doesn't freeze the GUI when using
def sleep(length_ms):
    loop = QEventLoop()
    QTimer.singleShot(length_ms, loop.quit)
    loop.exec_()


def type_bakkes_command(input_string, print_message=None):
    pause_time_ms = int(10)

    # press f6 to bring up the bakkes_mod console
    keyboard.press(Key.f6)
    sleep(pause_time_ms)
    keyboard.release(Key.f6)
    if print_message is not None:
        print(print_message + "\n")

    # type each character in the input string
    for character in input_string:
        keyboard.type(character)
        sleep(pause_time_ms)

    sleep(3 * pause_time_ms)

    # press enter
    keyboard.press(Key.enter)
    sleep(3 * pause_time_ms)
    keyboard.release(Key.enter)

    # then close the console again
    keyboard.press(Key.f6)
    sleep(3 * pause_time_ms)
    keyboard.release(Key.f6)

    # presses escape to close the console, sometimes f6 doesnt work
    sleep(4000)
    keyboard.press(Key.esc)
    sleep(3 * pause_time_ms)
    keyboard.release(Key.esc)


class Window(QMainWindow):
    """Main Window."""

    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setWindowTitle('PythonRocketTrainer')

        # colours and stylesheet definitions
        self.colour_1 = "77878B"
        self.colour_2 = "305252"
        self.colour_3 = "373E40"
        self.colour_4 = "488286"
        self.colour_5 = "B7D5D4"
        self.text_colour_1 = "color: #2C4251"
        # self.training_button_background = "background-color: #C1C1C1"
        self.training_button_background = "background-color: #3C3C3C"
        self.training_button_style_sheet = "color: #F5F5F5; background-color: #3C3C3C"
        # self.training_button_style_sheet = "color: #2C4251; background-color: #C1C1C1"
        self.setStyleSheet("color: #2C4251; background-color: #" + "FBF5F3")

        # C:\\users\conno\PycharmProjects\RocketTrainer\maps
        # variable init
        with open('map_dir.txt', "r") as f:
            map_dir = f.readlines()[0]
            print(map_dir)
            f.close()

        self.map_dir = map_dir
        self.plan_manager = PlanManager(self.map_dir)

        self.current_training_plan = []
        self.which_box_displayed = 0
        self._init_plan_matrix()
        self.times = []

        # timing parameters
        self.total_time = 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.second_clock)

        self.total_training_time = 0
        self.is_paused = False
        self.counter = 0
        self.is_started = False

        # general layout
        self.generalLayout = QVBoxLayout()
        self.generalLayout.setAlignment(Qt.AlignTop)
        self._centralWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)
        self._centralWidget.setLayout(self.generalLayout)

        # add display elements
        self._add_header()
        self._create_blank_space(5)
        self._add_training_plan_buttons()
        self._add_control_buttons()
        self._add_timers()
        self._create_blank_space(5)
        self._populate_plan_boxes()
        self._create_tool_bar()
        # starting_dir = cmds.workspace(q=True, rootDirectory=True)

    # initialise methods
    def _init_plan_matrix(self):
        max_y = self.plan_manager.largest_plan_dims
        max_x = 4
        self.plan_matrix = []
        for y in range(max_y):
            y_blanks = []
            for x in range(max_x):
                y_blanks.append("")

            self.plan_matrix.append(y_blanks)

    # timing operations
    def second_clock(self):
        print(self.counter)
        if not self.is_paused:
            self.counter += 1
            self.update_time_boxes(self.counter)
            self.start_training(self.counter)

        else:
            pass

    def update_time_boxes(self, counter):

        def time_cleaner(input_time, time_format):
            # takes a time in second and cleans it to display int minutes as a string
            if time_format == "min":
                return str(int(math.floor(input_time/60))) + " min"

            if time_format == "sec":
                minutes = int(math.floor(input_time / 60))
                seconds = int(input_time - minutes*60)

                return str(minutes) + " min, " + str(seconds) + " secs"

        # this calculates the total remaining time left in the session
        remaining_total_time = time_cleaner(self.total_training_time - counter, time_format="min")
        # and updates the relevant timer
        self.total_training_time_timer.setText(remaining_total_time)

        # this calculates the next time at which a transition in training will occur
        next_training_time = min(x for x in self.times if x > counter)
        remaining_exercise_time = time_cleaner(next_training_time - counter, time_format="sec")
        self.current_training_time_timer.setText(remaining_exercise_time)

    def start_timer(self):
        self.timer.start(1000)

    # start the training
    def start_training(self, counter):

        # index to update the current coloured box within the plan_boxes
        box_index = 0

        # if counter is 0 then we need to initiate the training, define all the consts we need etc.
        if counter == 0:

            self.is_started = True

            # we multiply by 60 to get the times in seconds
            self.times = [60 * exercise.exercise_time for exercise in self.current_training_plan[1]]
            print(self.times)
            # we need the times to be cumulative so that there always exists a unique match to counter

            self.times = list(np.cumsum(self.times))
            print([x/60 for x in self.times])
            # start the training session
            sleep(5000)
            self.update_plan_boxes(box_colour_index=box_index)
            box_index += 1
            self.start_timer()
            first_exercise = self.current_training_plan[1][0]
            type_bakkes_command(first_exercise.run_command)

        # this means that a transition time has occurred: we should change the training plan
        if counter in self.times:
            index = self.times.index(counter)

            # we removed 0 from the list of times, because of all the __init__ which is specific to it
            # we need to increase index by 1 to account for this
            index += 1
            current_exercise = self.current_training_plan[1][index]
            box_index += 1
            self.update_plan_boxes(box_colour_index=box_index)
            type_bakkes_command(current_exercise.run_command)

    # build the elements of the GUI
    def _add_header(self):
        self.large_header = QLabel("      Python RL Training      ")
        self.large_header.setFont(QFont('Helvetica Bold', 39))
        self.large_header.setAlignment(Qt.AlignCenter)
        self.large_header.setStyleSheet(self.text_colour_1)
        self.generalLayout.addWidget(self.large_header)

    def _add_training_plan_buttons(self):

        training_header_buttons_layout = QHBoxLayout()

        training_plan_1_button = QPushButton(self.plan_manager.plans[0][0])
        training_plan_1_button.setStyleSheet(self.training_button_style_sheet)
        training_plan_1_button.setFont(QFont('Helvetica Bold', 10))

        training_plan_2_button = QPushButton(self.plan_manager.plans[1][0])
        training_plan_2_button.setStyleSheet(self.training_button_style_sheet)
        training_plan_2_button.setFont(QFont('Helvetica Bold', 10))

        training_plan_3_button = QPushButton(self.plan_manager.plans[2][0])
        training_plan_3_button.setStyleSheet(self.training_button_style_sheet)
        training_plan_3_button.setFont(QFont('Helvetica Bold', 10))

        training_plan_4_button = QPushButton(self.plan_manager.plans[3][0])
        training_plan_4_button.setStyleSheet(self.training_button_style_sheet)
        training_plan_4_button.setFont(QFont('Helvetica Bold', 10))

        def push_training_button_1():
            self.current_training_plan = self.plan_manager.plans[0]
            self.which_box_displayed = 0
            self.update_plan_boxes()

        def push_training_button_2():
            self.current_training_plan = self.plan_manager.plans[1]
            self.which_box_displayed = 1
            self.update_plan_boxes()

        def push_training_button_3():
            self.current_training_plan = self.plan_manager.plans[2]
            self.which_box_displayed = 2
            self.update_plan_boxes()

        def push_training_button_4():
            self.current_training_plan = self.plan_manager.plans[3]
            self.which_box_displayed = 3
            self.update_plan_boxes()

        training_plan_1_button.clicked.connect(push_training_button_1)
        training_plan_2_button.clicked.connect(push_training_button_2)
        training_plan_3_button.clicked.connect(push_training_button_3)
        training_plan_4_button.clicked.connect(push_training_button_4)

        training_header_buttons_layout.addWidget(training_plan_1_button)
        training_header_buttons_layout.addWidget(training_plan_2_button)
        training_header_buttons_layout.addWidget(training_plan_3_button)
        training_header_buttons_layout.addWidget(training_plan_4_button)

        self.generalLayout.addLayout(training_header_buttons_layout)

    def _add_control_buttons(self):
        action_button_layout = QHBoxLayout()

        # Start/Exit button
        start_stop_button = QPushButton("Start")
        start_stop_button.setStyleSheet("color: #FBF5F3; background-color: #FF5A5F")
        start_stop_button.setFont(QFont('Helvetica Bold', 10))

        def start_stop_button_action():
            if start_stop_button.text() == "Start":
                start_stop_button.setText("Exit")
                start_stop_button.setStyleSheet("color: #FBF5F3; background-color: #FF5A5F")
                if not self.current_training_plan:
                    # potential to add a text display which lets the user know they haven't selected a pack
                    pass
                else:
                    self.counter = 0
                    self.start_training(self.counter)

            elif start_stop_button.text() == "Exit":
                sys.exit()

        start_stop_button.clicked.connect(start_stop_button_action)

        # shuffle button
        shuffled_button = QPushButton("Shuffle")
        shuffled_button.setStyleSheet("color: #FBF5F3; background-color: #087E8B")
        shuffled_button.setFont(QFont('Helvetica Bold', 10))

        def shuffled_action():
            random.shuffle(self.current_training_plan[1])
            self.update_plan_boxes()

        shuffled_button.clicked.connect(shuffled_action)

        # pause button
        self.play_pause_button = QPushButton("Pause")
        self.play_pause_button.setStyleSheet("color: #FBF5F3; background-color: #FF5A5F")
        self.play_pause_button.setFont(QFont('Helvetica Bold', 10))

        def pause_resume():
            if self.is_paused:
                self.is_paused = False
                self.play_pause_button.setText("Pause")
            elif not self.is_paused:
                self.is_paused = True
                self.play_pause_button.setText("Resume")

        self.play_pause_button.clicked.connect(pause_resume)

        # re-randomise training plans
        re_random_button = QPushButton("Re-Roll")
        re_random_button.setStyleSheet("color: #FBF5F3; background-color: #087E8B")
        re_random_button.setFont(QFont('Helvetica Bold', 10))
        re_random_button.clicked.connect(self.re_roll_training_items)

        # timers

        # add buttons
        action_button_layout.addWidget(start_stop_button)
        action_button_layout.addWidget(self.play_pause_button)
        action_button_layout.addWidget(shuffled_button)
        action_button_layout.addWidget(re_random_button)

        action_button_layout.setAlignment(Qt.AlignCenter)
        self.generalLayout.addLayout(action_button_layout)

    def _add_timers(self):
        timer_layout = QHBoxLayout()

        # timer_stylesheets = "color: #F5F5F5; background-color: #6369D1"
        timer_stylesheets = self.text_colour_1

        # label for total time timer
        total_timer_1_text = QLabel("Total Training Time:")
        total_timer_1_text.setFont(QFont('Helvetica Bold', 10))
        total_timer_1_text.setAlignment(Qt.AlignCenter)
        total_timer_1_text.setStyleSheet(self.text_colour_1)
        timer_layout.addWidget(total_timer_1_text)

        # timer for the total training
        self.total_training_time_timer = QLineEdit()
        self.total_training_time_timer.setText("-")
        self.total_training_time_timer.setReadOnly(True)
        self.total_training_time_timer.setAlignment(Qt.AlignCenter)
        self.total_training_time_timer.setFont(QFont('Helvetica Bold', 10))
        self.total_training_time_timer.setStyleSheet(timer_stylesheets)
        timer_layout.addWidget(self.total_training_time_timer)

        # label for the current exercise timer
        current_training_text = QLabel("Current Exercise Time:")
        current_training_text.setFont(QFont('Helvetica Bold', 10))
        current_training_text.setAlignment(Qt.AlignCenter)
        current_training_text.setStyleSheet(self.text_colour_1)
        timer_layout.addWidget(current_training_text)

        # timer for the current exercise
        self.current_training_time_timer = QLineEdit()
        self.current_training_time_timer.setText("-")
        self.current_training_time_timer.setReadOnly(True)
        self.current_training_time_timer.setAlignment(Qt.AlignCenter)
        self.current_training_time_timer.setFont(QFont('Helvetica Bold', 10))
        self.current_training_time_timer.setStyleSheet(timer_stylesheets)
        timer_layout.addWidget(self.current_training_time_timer)

        self.generalLayout.addLayout(timer_layout)

    def _create_blank_space(self, height):
        self.large_header = QLabel("")
        self.large_header.setFont(QFont('Helvetica Bold', height))
        self.generalLayout.addWidget(self.large_header)

    def _populate_plan_boxes(self):

        grid = QGridLayout()

        # TITLES
        titles = ["Type", "Category", "Name", "Time"]
        lab_1 = QLabel(titles[0])
        lab_1.setAlignment(Qt.AlignCenter)
        grid.addWidget(lab_1, 1, 1)
        lab_2 = QLabel(titles[1])
        lab_2.setAlignment(Qt.AlignCenter)
        grid.addWidget(lab_2, 1, 2)
        lab_3 = QLabel(titles[2])
        lab_3.setAlignment(Qt.AlignCenter)
        grid.addWidget(lab_3, 1, 3)
        lab_4 = QLabel(titles[3])
        lab_4.setAlignment(Qt.AlignCenter)
        grid.addWidget(lab_4, 1, 4)

        # had issues creating this programmatically, so resorted to manually creating each of the boxes. It sucks but
        # it was late. The programmatic method of generation is commented out at the bottom of this complete mess.
        self.box_0_0 = QLineEdit()
        self.box_0_0.setReadOnly(True)
        self.box_0_0.setAlignment(Qt.AlignCenter)
        self.box_0_0.setText(self.plan_matrix[0][0])
        grid.addWidget(self.box_0_0, 2, 1)

        self.box_0_1 = QLineEdit()
        self.box_0_1.setReadOnly(True)
        self.box_0_1.setAlignment(Qt.AlignCenter)
        self.box_0_1.setText(self.plan_matrix[0][1])
        grid.addWidget(self.box_0_1, 2, 2)

        self.box_0_2 = QLineEdit()
        self.box_0_2.setReadOnly(True)
        self.box_0_2.setAlignment(Qt.AlignCenter)
        self.box_0_2.setText(self.plan_matrix[0][2])
        grid.addWidget(self.box_0_2, 2, 3)

        self.box_0_3 = QLineEdit()
        self.box_0_3.setReadOnly(True)
        self.box_0_3.setAlignment(Qt.AlignCenter)
        self.box_0_3.setText(self.plan_matrix[0][3])
        grid.addWidget(self.box_0_3, 2, 4)

        self.box_1_0 = QLineEdit()
        self.box_1_0.setReadOnly(True)
        self.box_1_0.setAlignment(Qt.AlignCenter)
        self.box_1_0.setText(self.plan_matrix[1][0])
        grid.addWidget(self.box_1_0, 3, 1)

        self.box_1_1 = QLineEdit()
        self.box_1_1.setReadOnly(True)
        self.box_1_1.setAlignment(Qt.AlignCenter)
        self.box_1_1.setText(self.plan_matrix[1][1])
        grid.addWidget(self.box_1_1, 3, 2)

        self.box_1_2 = QLineEdit()
        self.box_1_2.setReadOnly(True)
        self.box_1_2.setAlignment(Qt.AlignCenter)
        self.box_1_2.setText(self.plan_matrix[1][2])
        grid.addWidget(self.box_1_2, 3, 3)

        self.box_1_3 = QLineEdit()
        self.box_1_3.setReadOnly(True)
        self.box_1_3.setAlignment(Qt.AlignCenter)
        self.box_1_3.setText(self.plan_matrix[1][3])
        grid.addWidget(self.box_1_3, 3, 4)

        ###########

        self.box_2_0 = QLineEdit()
        self.box_2_0.setReadOnly(True)
        self.box_2_0.setAlignment(Qt.AlignCenter)
        self.box_2_0.setText(self.plan_matrix[2][0])
        grid.addWidget(self.box_2_0, 4, 1)

        self.box_2_1 = QLineEdit()
        self.box_2_1.setReadOnly(True)
        self.box_2_1.setAlignment(Qt.AlignCenter)
        self.box_2_1.setText(self.plan_matrix[2][1])
        grid.addWidget(self.box_2_1, 4, 2)

        self.box_2_2 = QLineEdit()
        self.box_2_2.setReadOnly(True)
        self.box_2_2.setAlignment(Qt.AlignCenter)
        self.box_2_2.setText(self.plan_matrix[2][2])
        grid.addWidget(self.box_2_2, 4, 3)

        self.box_2_3 = QLineEdit()
        self.box_2_3.setReadOnly(True)
        self.box_2_3.setAlignment(Qt.AlignCenter)
        self.box_2_3.setText(self.plan_matrix[2][3])
        grid.addWidget(self.box_2_3, 4, 4)

        ###########

        self.box_3_0 = QLineEdit()
        self.box_3_0.setReadOnly(True)
        self.box_3_0.setAlignment(Qt.AlignCenter)
        self.box_3_0.setText(self.plan_matrix[3][0])
        grid.addWidget(self.box_3_0, 5, 1)

        self.box_3_1 = QLineEdit()
        self.box_3_1.setReadOnly(True)
        self.box_3_1.setAlignment(Qt.AlignCenter)
        self.box_3_1.setText(self.plan_matrix[3][1])
        grid.addWidget(self.box_3_1, 5, 2)

        self.box_3_2 = QLineEdit()
        self.box_3_2.setReadOnly(True)
        self.box_3_2.setAlignment(Qt.AlignCenter)
        self.box_3_2.setText(self.plan_matrix[3][2])
        grid.addWidget(self.box_3_2, 5, 3)

        self.box_3_3 = QLineEdit()
        self.box_3_3.setReadOnly(True)
        self.box_3_3.setAlignment(Qt.AlignCenter)
        self.box_3_3.setText(self.plan_matrix[3][3])
        grid.addWidget(self.box_3_3, 5, 4)

        ###########

        self.box_4_0 = QLineEdit()
        self.box_4_0.setReadOnly(True)
        self.box_4_0.setAlignment(Qt.AlignCenter)
        self.box_4_0.setText(self.plan_matrix[4][0])
        grid.addWidget(self.box_4_0, 6, 1)

        self.box_4_1 = QLineEdit()
        self.box_4_1.setReadOnly(True)
        self.box_4_1.setAlignment(Qt.AlignCenter)
        self.box_4_1.setText(self.plan_matrix[4][1])
        grid.addWidget(self.box_4_1, 6, 2)

        self.box_4_2 = QLineEdit()
        self.box_4_2.setReadOnly(True)
        self.box_4_2.setAlignment(Qt.AlignCenter)
        self.box_4_2.setText(self.plan_matrix[4][2])
        grid.addWidget(self.box_4_2, 6, 3)

        self.box_4_3 = QLineEdit()
        self.box_4_3.setReadOnly(True)
        self.box_4_3.setAlignment(Qt.AlignCenter)
        self.box_4_3.setText(self.plan_matrix[4][3])
        grid.addWidget(self.box_4_3, 6, 4)

        ###########

        self.box_5_0 = QLineEdit()
        self.box_5_0.setReadOnly(True)
        self.box_5_0.setAlignment(Qt.AlignCenter)
        self.box_5_0.setText(self.plan_matrix[5][0])
        grid.addWidget(self.box_5_0, 7, 1)

        self.box_5_1 = QLineEdit()
        self.box_5_1.setReadOnly(True)
        self.box_5_1.setAlignment(Qt.AlignCenter)
        self.box_5_1.setText(self.plan_matrix[5][1])
        grid.addWidget(self.box_5_1, 7, 2)

        self.box_5_2 = QLineEdit()
        self.box_5_2.setReadOnly(True)
        self.box_5_2.setAlignment(Qt.AlignCenter)
        self.box_5_2.setText(self.plan_matrix[5][2])
        grid.addWidget(self.box_5_2, 7, 3)

        self.box_5_3 = QLineEdit()
        self.box_5_3.setReadOnly(True)
        self.box_5_3.setAlignment(Qt.AlignCenter)
        self.box_5_3.setText(self.plan_matrix[5][3])
        grid.addWidget(self.box_5_3, 7, 4)

        self.generalLayout.addLayout(grid)
        """for x in range(max_x):
            for y in range(max_y):
                _box = QLineEdit()
                _box.setReadOnly(True)
                _box.setText(self.plan_matrix[x][y])
                grid.addWidget(_box, x + 2, y + 1)
        self.generalLayout.addLayout(grid)"""

    def _create_tool_bar(self):
        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction("Select Map Directory", self.directory_selection)
        tools.addAction('Exit', self.close)

    # dynamic operations
    def directory_selection(self):
        map_dir = str(QFileDialog.getExistingDirectory(self, caption='Select Map Directory'))
        self.map_dir = map_dir
        self.plan_manager.change_map_dir(self.map_dir)

        # wipe the map directory file
        open('map_dir.txt', 'w').close()

        # write the new path to the file
        with open('map_dir.txt', 'w') as f:
            f.write(str(self.map_dir))

    def re_roll_training_items(self):
        self.plan_manager.reset_training_objects(self.map_dir)
        self.current_training_plan = self.plan_manager.plans[self.which_box_displayed]
        self.update_plan_boxes()

    def update_plan_boxes(self, box_colour_index=None):
        self.total_training_time = sum([60 * exercise.exercise_time for exercise in self.current_training_plan[1]])
        self.total_training_time_timer.setText(str(int(self.total_training_time/60)) + " min")

        # self.plan_matrix and update based on what current_training_plan is
        for i in range(len(self.current_training_plan[1])):
            training_object = self.current_training_plan[1][i]

            _type = str(training_object.training_type)
            _cat = str(training_object.category)
            _name = str(training_object.name)
            _time = str(training_object.exercise_time)

            self.plan_matrix[i][0] = _type
            self.plan_matrix[i][1] = _cat
            self.plan_matrix[i][2] = _name
            self.plan_matrix[i][3] = _time

        if len(self.current_training_plan[1]) < self.plan_manager.largest_plan_dims:

            for j in range(len(self.current_training_plan[1]), self.plan_manager.largest_plan_dims):
                self.plan_matrix[j][0] = ""
                self.plan_matrix[j][1] = ""
                self.plan_matrix[j][2] = ""
                self.plan_matrix[j][3] = ""

        # colouring the current exercise in a different stylesheet from the rest of the exercises
        stylesheet_array = ["" for _ in range(6)]
        current_exercise_stylesheet = "color: #FBF5F3; background-color: #087E8B"
        if box_colour_index is not None:
            stylesheet_array[box_colour_index] = current_exercise_stylesheet

        self.box_0_0.setText(self.plan_matrix[0][0])
        self.box_0_1.setText(self.plan_matrix[0][1])
        self.box_0_2.setText(self.plan_matrix[0][2])
        self.box_0_3.setText(self.plan_matrix[0][3])
        self.box_0_0.setStyleSheet(stylesheet_array[0])
        self.box_0_1.setStyleSheet(stylesheet_array[0])
        self.box_0_2.setStyleSheet(stylesheet_array[0])
        self.box_0_3.setStyleSheet(stylesheet_array[0])

        self.box_1_0.setText(self.plan_matrix[1][0])
        self.box_1_1.setText(self.plan_matrix[1][1])
        self.box_1_2.setText(self.plan_matrix[1][2])
        self.box_1_3.setText(self.plan_matrix[1][3])
        self.box_1_0.setStyleSheet(stylesheet_array[1])
        self.box_1_1.setStyleSheet(stylesheet_array[1])
        self.box_1_2.setStyleSheet(stylesheet_array[1])
        self.box_1_3.setStyleSheet(stylesheet_array[1])

        self.box_2_0.setText(self.plan_matrix[2][0])
        self.box_2_1.setText(self.plan_matrix[2][1])
        self.box_2_2.setText(self.plan_matrix[2][2])
        self.box_2_3.setText(self.plan_matrix[2][3])
        self.box_2_0.setStyleSheet(stylesheet_array[2])
        self.box_2_1.setStyleSheet(stylesheet_array[2])
        self.box_2_2.setStyleSheet(stylesheet_array[2])
        self.box_2_3.setStyleSheet(stylesheet_array[2])

        self.box_3_0.setText(self.plan_matrix[3][0])
        self.box_3_1.setText(self.plan_matrix[3][1])
        self.box_3_2.setText(self.plan_matrix[3][2])
        self.box_3_3.setText(self.plan_matrix[3][3])
        self.box_3_0.setStyleSheet(stylesheet_array[3])
        self.box_3_1.setStyleSheet(stylesheet_array[3])
        self.box_3_2.setStyleSheet(stylesheet_array[3])
        self.box_3_3.setStyleSheet(stylesheet_array[3])

        self.box_4_0.setText(self.plan_matrix[4][0])
        self.box_4_1.setText(self.plan_matrix[4][1])
        self.box_4_2.setText(self.plan_matrix[4][2])
        self.box_4_3.setText(self.plan_matrix[4][3])
        self.box_4_0.setStyleSheet(stylesheet_array[4])
        self.box_4_1.setStyleSheet(stylesheet_array[4])
        self.box_4_2.setStyleSheet(stylesheet_array[4])
        self.box_4_3.setStyleSheet(stylesheet_array[4])

        self.box_5_0.setText(self.plan_matrix[5][0])
        self.box_5_1.setText(self.plan_matrix[5][1])
        self.box_5_2.setText(self.plan_matrix[5][2])
        self.box_5_3.setText(self.plan_matrix[5][3])
        self.box_5_0.setStyleSheet(stylesheet_array[5])
        self.box_5_1.setStyleSheet(stylesheet_array[5])
        self.box_5_2.setStyleSheet(stylesheet_array[5])
        self.box_5_3.setStyleSheet(stylesheet_array[5])


# create the GUI and execute the code
if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = Window()
    win.show()
    sys.exit(app.exec_())
