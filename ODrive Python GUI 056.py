import odrive
from odrive.utils import *
import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
from tktooltip import ToolTip
import time

width = 1000
height = 500

currentrow = 0
currentsection = 0

###################################### odrive dicts ######################################

motortypes = {"MOTOR_TYPE_HIGH_CURRENT": 0, "MOTOR_TYPE_GIMBAL": 2, "MOTOR_TYPE_ACIM": 3}
axisstates = {"UNDEFINED": 0, "IDLE": 1, "STARTUP_SEQUENCE": 2, "FULL_CALIBRATION_SEQUENCE": 3, "MOTOR_CALIBRATION": 4, "ENCODER_INDEX_SEARCH": 6, "ENCODER_OFFSET_CALIBRATION": 7, "CLOSED_LOOP_CONTROL": 8, "LOCKIN_SPIN": 9, "INPUT_TORQUE_CONTROL": 10, "INPUT_VOLTAGE_CONTROL": 11, "CURRENT_CONTROL": 12, "VELOCITY_CONTROL": 13, "POSITION_CONTROL": 14, "TRAJECTORY_CONTROL": 15, "DISCOVERING_USB": 16, "UNKNOWN": 255}
encodermode = {"ENCODER_MODE_INCREMENTAL": 0, "ENCODER_MODE_HALL": 1, "ENCODER_MODE_SINCOS": 2, "ENCODER_MODE_SPI_ABS_CUI": 256, "ENCODER_MODE_SPI_ABS_AMS": 257, "ENCODER_MODE_SPI_ABS_AEAT": 258, "ENCODER_MODE_SPI_ABS_AEAT_MARK": 259, "ENCODER_MODE_SPI_ABS_CUI_2048": 260, "ENCODER_MODE_SPI_ABS_CUI_4096": 261, "ENCODER_MODE_SPI_ABS_CUI_8192": 262, "ENCODER_MODE_SPI_ABS_AMS_512": 263, "ENCODER_MODE_SPI_ABS_AMS_1024": 264, "ENCODER_MODE_SPI_ABS_AMS_2048": 265, "ENCODER_MODE_SPI_ABS_AMS_4096": 266, "ENCODER_MODE_SPI_ABS_AMS_8192": 267, "ENCODER_MODE_SPI_ABS_AMS_16384": 268, "ENCODER_MODE_SPI_ABS_AMS_32768": 269, "ENCODER_MODE_SPI_ABS_AMS_65536": 270, "ENCODER_MODE_SPI_ABS_AMS_131072": 271, "ENCODER_MODE_SPI_ABS_AMS_262144": 272, "ENCODER_MODE_SPI_ABS_AMS_524288": 273, "ENCODER_MODE_SPI_ABS_AMS_1048576": 274, "ENCODER_MODE_SPI_ABS_AMS_2097152": 275, "ENCODER_MODE_SPI_ABS_AMS_4194304": 276, "ENCODER_MODE_SPI_ABS_AMS_8388608": 277, "ENCODER_MODE_SPI_ABS_AMS_16777216": 278, "ENCODER_MODE_SPI_ABS_AMS_33554432": 279, "ENCODER_MODE_SPI_ABS_AMS_67108864": 280, "ENCODER_MODE_SPI_ABS_AMS_134217728": 281, "ENCODER_MODE_SPI_ABS_AMS_268435456": 282, "ENCODER_MODE_SPI_ABS_AMS_MASK": 4294901760}
controlmodes = {"CTRL_MODE_VOLTAGE_CONTROL": 0, "CTRL_MODE_TORQUE_CONTROL": 1, "CTRL_MODE_VELOCITY_CONTROL": 2, "CTRL_MODE_POSITION_CONTROL": 3, "CTRL_MODE_TRAJECTORY_CONTROL": 4}
inputmodes = {"INPUT_MODE_INACTIVE": 0, "INPUT_MODE_PASSTHROUGH": 1, "INPUT_MODE_VEL_RAMP": 2, "INPUT_MODE_POS_FILTER": 3}
bools = { "True": 1, "False": 0}
board_errors = {"NONE": 0, "CONTROL_ITERATION_MISSED": 1, "DC_BUS_UNDER_VOLTAGE": 2, "DC_BUS_OVER_VOLTAGE": 4, "DC_BUS_OVER_REGEN_CURRENT": 8, "DC_BUS_OVER_CURRENT": 16, "BRAKE_DEADTIME_VIOLATION": 32, "BRAKE_DUTY_CYCLE_NAN": 64, "INVALID_BRAKE_RESISTANCE": 128}
axis_errors = {"NONE": 0, "INVALID_STATE": 1, "WATCHDOG_TIMER_EXPIRED": 2048, "MIN_ENDSTOP_PRESSED": 4096, "MAX_ENDSTOP_PRESSED": 8192, "ESTOP_REQUESTED": 16384, "HOMING_WITHOUT_ENDSTOP": 131072, "OVER_TEMP": 262144, "UNKNOWN_POSITION": 524288}
motor_errors = {"NONE": 0, "PHASE_RESISTANCE_OUT_OF_RANGE": 1, "PHASE_INDUCTANCE_OUT_OF_RANGE": 2, "DRV_FAULT": 8, "CONTROL_DEADLINE_MISSED": 16, "MODULATION_MAGNITUDE": 128, "CURRENT_SENSE_SATURATION": 1024, "CURRENT_LIMIT_VIOLATION": 4096, "MODULATION_IS_NAN": 65536, "MOTOR_THERMISTOR_OVER_TEMP": 131072, "FET_THERMISTOR_OVER_TEMP": 262144, "TIMER_UPDATE_MISSED": 524288, "CURRENT_MEASUREMENT_UNAVAILABLE": 1048576, "CONTROLLER_FAILED": 2097152, "I_BUS_OUT_OF_RANGE": 4194304, "BRAKE_RESISTOR_DISARMED": 8388608, "SYSTEM_LEVEL": 16777216, "BAD_TIMING": 33554432, "UNKNOWN_PHASE_ESTIMATE": 67108864, "UNKNOWN_PHASE_VEL": 134217728, "UNKNOWN_TORQUE": 268435456, "UNKNOWN_CURRENT_COMMAND": 536870912, "UNKNOWN_CURRENT_MEASUREMENT": 1073741824, "UNKNOWN_VBUS_VOLTAGE": 2147483648, "UNKNOWN_VOLTAGE_COMMAND": 4294967296, "UNKNOWN_GAINS": 8589934592, "CONTROLLER_INITIALIZING": 17179869184, "UNBALANCED_PHASES": 34359738368}
encoder_errors = {"NONE": 0, "UNSTABLE_GAIN": 1, "CPR_POLEPAIRS_MISMATCH": 2, "NO_RESPONSE": 4, "UNSUPPORTED_ENCODER_MODE": 8, "ILLEGAL_HALL_STATE": 16, "INDEX_NOT_FOUND_YET": 32, "ABS_SPI_TIMEOUT": 64, "ABS_SPI_COM_FAIL": 128, "ABS_SPI_NOT_READY": 256, "HALL_NOT_CALIBRATED_YET": 512}
controller_errors = {"NONE": 0, "OVERSPEED": 1, "INVALID_INPUT_MODE": 2, "UNSTABLE_GAIN": 4, "INVALID_MIRROR_AXIS": 8, "INVALID_LOAD_ENCODER": 16, "INVALID_ESTIMATE": 32, "INVALID_CIRCULAR_RANGE": 64, "SPINOUT_DETECTED": 128}

######################################## objects #########################################

error_objects = []

##################################### dict functions #####################################

def getkey(value, dict):
    matching_keys = [key for key, val in dict.items() if val == value]
    if len(matching_keys) == 1:
        return matching_keys[0]
    elif len(matching_keys) == 0:
        raise ValueError(f"No key found for value {value}")
    else:
        raise ValueError(f"Multiple keys found for value {value}: {matching_keys}")

def getvalue(key, dict):
    matching_value = dict.get(key)
    if matching_value is not None:
        return matching_value
    else:
        raise ValueError(f"No value found for key {key}")

######################################### functions #########################################

def labelobject(container, label_text, info, row, column):
    label = tk.Button(container)
    label["bg"] = "#f0f0f0"
    label["font"] = tkFont.Font(family='Consolas', size=16)
    label["fg"] = "#000000"
    label["anchor"] = "w"
    label["text"] = label_text
    label["relief"] = "flat"
    label.grid(row=row, column=column, sticky='ew', padx=4, pady=4)
    if info != "":
        ToolTip(label, msg=info, font=tkFont.Font(family='Consolas', size=16))
    return label

def labelframeobject(container, section_name, row, column):
    labelframe = tk.LabelFrame(container)
    labelframe["bg"] = "#f0f0f0"
    labelframe["fg"] = "#000000"
    labelframe["text"] = section_name
    labelframe.configure(font=tkFont.Font(family='Consolas', size=18, weight="bold"))
    labelframe.grid(row=row, column=column, sticky='ew', padx=4, pady=4)
    return labelframe

def entryobject(container, row, column):
    entry = tk.Entry(container)
    entry["borderwidth"] = "1px"
    entry["font"] = tkFont.Font(family='Consolas', size=16)
    entry["fg"] = "#333333"
    entry["justify"] = "center"
    entry["relief"] = "solid"
    entry.grid(row=row, column=column, sticky='nsew', padx=4, pady=4)
    return entry

def dropdownobject(container, row, column, options):
    variable = tk.StringVar(container)
    variable.set(options[0])
    dropdown = tk.OptionMenu(container, variable, *options)
    dropdown["relief"] = "solid"
    dropdown["borderwidth"] = "1px"
    dropdown["font"] = tkFont.Font(family='Consolas', size=16)
    container.nametowidget(dropdown.menuname).config(font=tkFont.Font(family='Consolas', size=16))
    dropdown["highlightthickness"] = "0px"
    dropdown.grid(row=row, column=column, sticky='nsew', padx=4, pady=4)
    return variable

def buttonobject(container, row, column, command, text, columnspan=1):
    button = tk.Button(container)
    button["bg"] = "#f0f0f0"
    button["font"] = tkFont.Font(family='Consolas', size=16)
    button["fg"] = "#000000"
    button["justify"] = "center"
    button["text"] = str(text)
    button["command"] = command
    button["relief"] = "solid"
    button["borderwidth"] = "1px"
    button.grid(row=row, column=column, sticky='nsew', padx=4, pady=4, columnspan=columnspan)
    return button

def sendbuttonobject(container, row, column, command):
    buttonobject(container, row, column, command, "send")

def displayobject(container, row, column, value):
    display = tk.Label(container)
    display["font"] = tkFont.Font(family='Consolas', size=16)
    display["fg"] = "#333333"
    display["anchor"] = "w"
    display["text"] = value
    display.grid(row=row, column=column, sticky='ewns', padx=4, pady=4)
    return display

def update_setting(path, value):
    exec(f'board.{path} = {value}')

def submit_entry(entry, display, path):
    value = entry.get()
    update_setting(path, value)
    display.configure(text=value)
    entry.delete(0, tk.END)

def submit_dropdown(variable, dict, display, path):
    value = getvalue(variable.get(), dict)
    update_setting(path, value)
    display.configure(text=getkey(value, dict))

def submit_requested_state(requested_state, dict, path):
    value = getvalue(requested_state, dict)
    update_setting(path, value)

def onsavereboot(container):
    global board
    container.grab_set()
    try:
        board.save_configuration()
    except:
        board = odrive.find_any()
        container.grab_release()

def onupdate_errors():
    global board
    for error in error_objects:
        display = error[0]
        dict = error[1]
        if dict == board_errors:
            try:
                update = getkey(board.error, board_errors)
            except:
                update = board.error
        elif dict == axis_errors:
            try:
                update = getkey(board.axis0.error, axis_errors)
            except:
                update = board.axis0.error
        elif dict == motor_errors:
            try:
                update = getkey(board.axis0.motor.error, motor_errors)
            except:
                update = board.axis0.motor.error
        elif dict == encoder_errors:
            try:
                update = getkey(board.axis0.encoder.error, encoder_errors)
            except:
                update = board.axis0.encoder.error
        elif dict == controller_errors:
            try:
                update = getkey(board.axis0.controller.error, controller_errors)
            except:
                update = board.axis0.controller.error
        display.configure(text=update)

def ontestposition():
    global board
    submit_requested_state("CTRL_MODE_POSITION_CONTROL", controlmodes, "axis0.controller.config.control_mode")
    board.axis0.controller.input_pos = 1
    time.sleep(1)
    board.axis0.controller.input_pos = 0

def ontestvelocity():
    global board
    submit_requested_state("CTRL_MODE_VELOCITY_CONTROL", controlmodes, "axis0.controller.config.control_mode")
    board.axis0.controller.input_vel = 1
    time.sleep(1)
    board.axis0.controller.input_vel = 0

###################################### GUI sections ######################################

def labelframe_section(container, name):
    global currentrow
    global currentsection
    currentrow = 0
    currentsection += 1
    labelframe = labelframeobject(container, name, currentsection, 0)
    return labelframe

######################################### GUI rows #########################################

def textbox_setting(container, label_text, path, info):
    global currentrow
    label = labelobject(container, label_text, info, currentrow, 0)
    entry = entryobject(container, currentrow, 1)
    display = displayobject(container, currentrow, 3, round(eval(f'board.{path}'), 5))
    button = sendbuttonobject(container, currentrow, 2, lambda: submit_entry(entry, display, path))
    currentrow += 1

def dropdown_setting(container, label_text, path, info, dict):
    global currentrow
    label = labelobject(container, label_text, info, currentrow, 0)
    variable = dropdownobject(container, currentrow, 1, list(dict.keys()))
    display = displayobject(container, currentrow, 3, getkey(eval(f'board.{path}'), dict))
    button = sendbuttonobject(container, currentrow, 2, lambda: submit_dropdown(variable, dict, display, path))
    currentrow += 1

def requested_state(container, requested_state, dict, column=0, columnspan=1):
    global currentrow
    button = buttonobject(container, currentrow, column, lambda: submit_requested_state(requested_state, dict, "axis0.requested_state"), requested_state, columnspan)
    currentrow += 1

def error_display(container, label_text, error, dict):
    global currentrow
    label = labelobject(container, label_text, "", currentrow, 0)
    try:
        errormessage = getkey(error, dict)
    except:
        errormessage = error
    display = displayobject(container, currentrow, 1, errormessage)
    error_objects.append([display, dict])
    currentrow += 1
    return display

def test_position(container, button_text, dict):
    global currentrow
    button = buttonobject(container, currentrow, 0, lambda: ontestposition(), button_text, 1)
    currentrow += 1

def test_velocity(container, label_text, dict):
    global currentrow
    button = buttonobject(container, currentrow, 0, lambda: ontestvelocity(), label_text, 1)
    currentrow += 1

def erase_configuration(container, column, columnspan):
    global currentrow
    erase_configuration_button = tk.Button(container)
    erase_configuration_button["bg"] = "#f0f0f0"
    erase_configuration_button["font"] = tkFont.Font(family='Consolas', size=16)
    erase_configuration_button["fg"] = "#000000"
    erase_configuration_button["justify"] = "center"
    erase_configuration_button["text"] = "Erase configuration"
    erase_configuration_button.grid(row=currentrow, column=column, columnspan=columnspan, sticky='ew', padx=4, pady=4)
    erase_configuration_button["command"] = lambda: eval("board.erase_configuration()")
    erase_configuration_button["relief"] = "solid"
    erase_configuration_button["borderwidth"] = "1px"
    currentrow += 1

def save_config_reboot(container, column, columnspan):
    global currentrow
    save_config_reboot_button = tk.Button(container)
    save_config_reboot_button["bg"] = "#f0f0f0"
    save_config_reboot_button["font"] = tkFont.Font(family='Consolas', size=16)
    save_config_reboot_button["fg"] = "#000000"
    save_config_reboot_button["justify"] = "center"
    save_config_reboot_button["text"] = "Save and Reboot"
    save_config_reboot_button.grid(row=currentrow, column=column, columnspan=columnspan, sticky='ew', padx=4, pady=4)
    save_config_reboot_button["command"] = lambda: onsavereboot(container)
    save_config_reboot_button["relief"] = "solid"
    save_config_reboot_button["borderwidth"] = "1px"
    currentrow += 1

def update_errors(container, column, columnspan):
    global currentrow
    update_errorsbutton = tk.Button(container)
    update_errorsbutton["bg"] = "#f0f0f0"
    update_errorsbutton["font"] = tkFont.Font(family='Consolas', size=16)
    update_errorsbutton["fg"] = "#000000"
    update_errorsbutton["justify"] = "center"
    update_errorsbutton["text"] = "Update errors"
    update_errorsbutton.grid(row=currentrow, column=column, columnspan=columnspan, sticky='ew', padx=4, pady=4)
    update_errorsbutton["command"] = lambda: onupdate_errors()
    update_errorsbutton["relief"] = "solid"
    update_errorsbutton["borderwidth"] = "1px"
    currentrow += 1

def clear_errors(container, column, columnspan):
    global currentrow
    clear_errorsbutton = tk.Button(container)
    clear_errorsbutton["bg"] = "#f0f0f0"
    clear_errorsbutton["font"] = tkFont.Font(family='Consolas', size=16)
    clear_errorsbutton["fg"] = "#000000"
    clear_errorsbutton["justify"] = "center"
    clear_errorsbutton["text"] = "Clear errors"
    clear_errorsbutton.grid(row=currentrow, column=column, columnspan=columnspan, sticky='ew', padx=4, pady=4)
    clear_errorsbutton["command"] = lambda: eval("board.clear_errors()")
    clear_errorsbutton["relief"] = "solid"
    clear_errorsbutton["borderwidth"] = "1px"
    currentrow += 1

############################################### app ###############################################

def on_configure(event):
    canvas.configure(scrollregion=canvas.bbox('all'))

width = 600
height = 400

window = tk.Tk()
window.title("ODrive 3.6 GUI")
window.geometry(f"{width}x{height}+0+0")
window.minsize(400, 200)

window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)

canvas = tk.Canvas(window)
canvas.grid(row=0, column=0, sticky=tk.NSEW)

scrollbar_y = ttk.Scrollbar(window, orient=tk.VERTICAL, command=canvas.yview)
scrollbar_y.grid(row=0, column=1, sticky='ns')
canvas.configure(yscrollcommand=scrollbar_y.set)

scrollbar_x = ttk.Scrollbar(window, orient=tk.HORIZONTAL, command=canvas.xview)
scrollbar_x.grid(row=1, column=0, sticky='ew')
canvas.configure(xscrollcommand=scrollbar_x.set)

frame = ttk.Frame(canvas)
canvas.create_window((0, 0), window=frame, anchor="nw")
frame.bind('<Configure>', on_configure)

window.bind('<MouseWheel>', lambda event: canvas.yview_scroll(int(-1 * (event.delta / 120)), "units"))
window.bind('<Shift-MouseWheel>', lambda event: canvas.xview_scroll(int(-1 * (event.delta / 120)), "units"))

canvas.yview_moveto(0)

boardlabel = labelobject(frame, "Searching for an ODrive", "", 0, 0)

def show_after_started():

    global board
    board = odrive.find_any()

    boardlabel.destroy()

    ###################################################### Essential Settings ######################################################

    section = labelframe_section(frame, "Essential Settings")

    erase_configuration(section, 0, 2)

    dropdown_setting(section, "Motor type", "axis0.motor.config.motor_type", "Select the type of motor you are using, brushless (BLDC), asynchronous (ACIM) or GIMBAL", motortypes)

    settings = [
        {"label": "Pole pairs", "path": "axis0.motor.config.pole_pairs", "info": "Number of pole pairs of the motor. This is equal to the number of permanent magnets in the rotor divided by 2."},
        {"label": "Current limit [A]", "path": "axis0.motor.config.current_lim", "info": "Maximum motor current, this should be less than the rated current of the motor. If you need more than 60A, you must change the current range."},
        {"label": "Calibration current [A]", "path": "axis0.motor.config.calibration_current", "info": "Current during motor calibration."},
        {"label": "Velocity limit [rev/s]", "path": "axis0.controller.config.vel_limit", "info": "Maximum velocity of the motor in rotations per second."},
        {"label": "Velocity limit tolerance [ratio]", "path": "axis0.controller.config.vel_limit_tolerance", "info": "Maximum velocity tolerance in rotations per second. This is used to determine when the axis is stationary."}
    ]

    for setting in settings:
        textbox_setting(section, setting["label"], setting["path"], setting["info"])
    
    dropdown_setting(section, "Enable brake resistor", "config.enable_brake_resistor", "Enable/disable the brake resistor.", bools)

    dropdown_setting(section, "Encoder type", "axis0.encoder.config.mode", "Select the type of encoder you are using.", encodermode)

    dropdown_setting(section, "Use index", "axis0.encoder.config.use_index", "Enable/disable the use of the index signal, this is only used for incremental encoders with index pulse.", bools)

    settings = [
        {"label": "Chip select GPIO pin", "path": "axis0.encoder.config.abs_spi_cs_gpio_pin", "info": "GPIO pin used for the SPI chip select signal. This is only used when using an SPI encoder. Power cycle may be required for changes to take effect."},
        {"label": "Encoder CPR", "path": "axis0.encoder.config.cpr", "info": "Number of counts per revolution, this is the same as 4 times the pulses per revolution (PPR)."}
    ]

    for setting in settings:
        textbox_setting(section, setting["label"], setting["path"], setting["info"])

    save_config_reboot(section, 1, 2)

    #################################################### Test settings ####################################################

    section = labelframe_section(frame, "Test settings")

    requested_state(section, "MOTOR_CALIBRATION", axisstates)
    requested_state(section, "ENCODER_OFFSET_CALIBRATION", axisstates)
    requested_state(section, "FULL_CALIBRATION_SEQUENCE", axisstates)
    requested_state(section, "CLOSED_LOOP_CONTROL", axisstates)
    requested_state(section, "IDLE", axisstates)
    test_position(section, "Test position", axisstates)
    test_velocity(section, "Test velocity", axisstates)

    ########################################################## Errors ##########################################################

    section = labelframe_section(frame, "Errors")

    update_errors(section, 0, 2)
    clear_errors(section, 0, 2)
    error_display(section, "Board error: ", board.error, board_errors)
    error_display(section, "Axis error: ", board.axis0.error, axis_errors)
    error_display(section, "Motor error: ", board.axis0.motor.error, motor_errors)
    error_display(section, "Encoder error: ", board.axis0.encoder.error, encoder_errors)
    error_display(section, "Controller error: ", board.axis0.controller.error, controller_errors)

    ######################################################## Troubleshooting ########################################################

    section = labelframe_section(frame, "Troubleshooting")
    
    settings = [
        {"label": "Calibration voltage [V]", "path": "axis0.motor.config.resistance_calib_max_voltage", "info": "The default value is not enough for high resistance motors. In general, you need resistance_calib_max_voltage > calibration_current * phase_resistance resistance_calib_max_voltage < 0.5 * vbus_voltage"},
        {"label": "Scan distance [rad]", "path": "axis0.encoder.config.calib_scan_distance", "info": "The length of the calibration movement, for low CPR position sensors, this value should be increased. If you want a scan distance of n mechanical revolutions, you need to set this to n * 2 * pi * pole pairs."},
        {"label": "Current control bandwidth", "path": "axis0.motor.config.current_control_bandwidth", "info": "Low KV motors may vibrate in position hold, reducing the current control bandwidth may solve this. This uses a biquad filter, so the resulting phase margin is actually half of what you set."},
        {"label": "Encoder bandwidth", "path": "axis0.encoder.config.bandwidth", "info": "Encoder bandwidth in radians per second. This is the cutoff frequency of the encoder velocity estimation. It should be set to a bit less than the electrical bandwidth of the motor."}
    ]

    for setting in settings:
        textbox_setting(section, setting["label"], setting["path"], setting["info"])

    save_config_reboot(section, 1, 2)

    ######################################################## Start-up sequence ########################################################

    section = labelframe_section(frame, "Start-up sequence")

    settings = [
        {"label": "Startup motor calibration", "path": "axis0.config.startup_motor_calibration", "info": "If true, the motor will be calibrated on startup."},
        {"label": "Save motor calibration", "path": "axis0.motor.config.pre_calibrated", "info": "If true, the motor calibration will be saved to the board so you don't need motor startup calibration. Before setting this to true, you must perform motor calibration."}
    ]

    for setting in settings:
        dropdown_setting(section, setting["label"], setting["path"], setting["info"], bools)

    requested_state(section, "MOTOR_CALIBRATION", axisstates, 0, 3)

    settings = [
        {"label": "Startup encoder offset calibration", "path": "axis0.config.startup_encoder_offset_calibration", "info": "If true, the encoder offset calibration will be performed on startup. "},
        {"label": "Save encoder offset calibration", "path": "axis0.encoder.config.pre_calibrated", "info": "If true, the encoder offset calibration will be saved to the board so you don't need encoder offset calibration. This can only be done when using an encoder with index, hall effect sensors or an absolute encoder, when using an encoder with index, you must also enable index search on startup.  Before setting this to true, you must perform encoder offset calibration."},
    ]

    for setting in settings:
        dropdown_setting(section, setting["label"], setting["path"], setting["info"], bools)

    requested_state(section, "ENCODER_OFFSET_CALIBRATION", axisstates, 0, 3)

    settings = [
        {"label": "Startup encoder index search", "path": "axis0.config.startup_encoder_index_search", "info": "If true, the encoder index search will be performed on startup."},
        {"label": "Startup closed loop control", "path": "axis0.config.startup_closed_loop_control", "info": "If true, the closed loop control will be started on startup"}
    ]

    for setting in settings:
        dropdown_setting(section, setting["label"], setting["path"], setting["info"], bools)

    save_config_reboot(section, 1, 2)

    ######################################################## Extra Settings ########################################################

    section = labelframe_section(frame, "Extra Settings")

    settings = [
        {"label": "Calibration current [A]", "path": "axis0.motor.config.calibration_current", "info": "Current during motor calibration."},
        {"label": "Torque constant [Nm/A]", "path": "axis0.motor.config.torque_constant", "info": "Torque constant KT of the motor, this is equal to 8.27/KV where KV is the motor velocity constant in rpm/Volt. If you want to input current instead of torque in torque control mode, you can set this to 1."},
        {"label": "Velocity limit [rev/s]", "path": "axis0.controller.config.vel_limit", "info": "Maximum velocity of the motor in rotations per second."},
        {"label": "Velocity limit tolerance [ratio]", "path": "axis0.controller.config.vel_limit_tolerance", "info": "Maximum velocity tolerance in rotations per second. This is used to determine when the axis is stationary."},
        {"label": "Current range [A]", "path": "axis0.motor.config.requested_current_range", "info": "This changes the amplifier gain to get a more accurate current measurement. The default is 60 A and the maximum is 120 A."}
    ]

    for setting in settings:
        textbox_setting(section, setting["label"], setting["path"], setting["info"])

    save_config_reboot(section, 1, 2)

    ######################################################## Application setup ########################################################

    section = labelframe_section(frame, "Application setup")

    dropdown_setting(section, "Control mode", "axis0.controller.config.control_mode", "Select the control mode you want to use", controlmodes)
    dropdown_setting(section, "Input mode", "axis0.controller.config.input_mode", "Select the input mode you want to use", inputmodes)

    save_config_reboot(section, 1, 2)

    ########################################################## PID tuning ##########################################################

    section = labelframe_section(frame, "PID tuning")

    settings = [
        {"label": "Position gain", "path": "axis0.controller.config.pos_gain", "info": "Position gain"},
        {"label": "Velocity gain", "path": "axis0.controller.config.vel_gain", "info": "Velocity gain"},
        {"label": "Velocity integral gain", "path": "axis0.controller.config.vel_integrator_gain", "info": "Velocity integral gain"}
    ]

    for setting in settings:
        textbox_setting(section, setting["label"], setting["path"], setting["info"])

    save_config_reboot(section, 1, 2)

window.after(100, show_after_started)

window.mainloop()
