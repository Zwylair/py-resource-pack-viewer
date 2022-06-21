from json import loads, JSONDecodeError
from os.path import getsize, split
from datetime import datetime
from random import getrandbits

import dearpygui.dearpygui as dpg

__version__ = 'Beta 21.06.2022a'

# Create a main window
dpg.create_context()
dpg.create_viewport(title=f'JPack Editor v.{__version__}', width=800, height=700)
dpg.set_viewport_small_icon('Icon.ico')


def get_rand_hash() -> str:
    return '%016x' % getrandbits(64)


def to_fixed(num_obj: float, digits=0) -> float:
    return float(f'{num_obj:.{digits}f}')


def __set_file_info(filename: str, file_path: str):
    data = ''
    # Set filename text
    data += f'{filename}:\n\t'

    # Set file weight text
    size = getsize(file_path)  # weight in bytes
    size /= 1024  # weight in kilobytes

    # Set file path
    data += f'{split(file_path)[0]}\n\t'

    # Set file weight text
    if size > 900:  # if size is more than 900 kb
        size /= 1024  # weight in megabytes
        size = to_fixed(size, 4)
        data += f'{size} (MB)'
    else:
        size = to_fixed(size, 4)
        data += f'{size} (KB)'

    dpg.set_value(opened_file_obj, data)


def __get_file_content(dpg_info: dict) -> str:
    file = dict(dpg_info['selections'])
    file_path = list(file.values())[0]
    filename = list(file.keys())[0]

    try:
        return_info = open(file_path).read()
    except UnicodeDecodeError:
        return_info = '[Error] Unable to read byte file'

    __set_file_info(filename, file_path)
    return return_info


def __write_log(text: str):
    current_time = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
    errors_logs = dpg.get_value(error_logs_text_obj)
    dpg.set_value(error_logs_text_obj, f'{errors_logs}[{current_time}]-{text}\n')


def __check_json_for_errors():
    try:
        loads(dpg.get_value(text_field_widget))
        __write_log('[INFO]: File successfully checked')
    except JSONDecodeError as error:
        __write_log(f'[ERROR]: {error}')


def __clear_text_field(obj: str):
    dpg.set_value(obj, '')


# block preview window
with dpg.window(width=128, height=128, no_title_bar=True, no_resize=True, no_close=True, no_move=True):
    dpg.add_text("Block preview\nwindow (BOX 1)", color=[120, 120, 120])

# json text preview window
with dpg.window(width=662, height=274, no_title_bar=True, no_resize=True, no_close=True, no_move=True, pos=[128, 0]):
    text_field_widget = dpg.add_input_text(width=640, height=235, multiline=True)

    # Register a file dialog
    with dpg.file_dialog(label='File Explorer', width=500, height=400, show=False, user_data=text_field_widget,
                         callback=lambda s, a, u: dpg.set_value(u, __get_file_content(a)),
                         tag="__filedialog", file_count=1):
        dpg.add_file_extension('.*')

    dpg.add_button(label='Select file', user_data='__filedialog',
                   callback=lambda s, a, u: dpg.configure_item(u, show=True), pos=[402, 246])

    dpg.add_button(label='Check json for errors', pos=[490, 246], callback=__check_json_for_errors)

# information window
with dpg.window(width=662, height=128, no_title_bar=True, no_resize=True, no_close=True, no_move=True, pos=[128, 274]):
    # Opened file info
    dpg.add_text('File info:\n\n')
    opened_file_obj = dpg.add_text('File not selected')
    opened_filename = ''
    opened_file_path = ''

# error window
with dpg.window(width=672, height=259, no_title_bar=True, no_resize=True, no_close=True, no_move=True, pos=[128, 402]):
    dpg.add_text('Program logs:')
    error_logs_text_obj = dpg.add_input_text(multiline=True, readonly=True, width=640, height=215)
    dpg.add_button(label='Clear logs', user_data=error_logs_text_obj, callback=lambda s, a, u: __clear_text_field(u), pos=[569, 9])


# Start the dpg
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
