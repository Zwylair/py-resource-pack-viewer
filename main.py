from json import load, JSONDecodeError
import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=700)


def get_file_content(dpg_info: dict) -> str:
    file = list(dpg_info['selections'].values())[0]
    try:
        dpg.set_value(opened_file_in_text_field, list(dpg_info['selections'].keys())[0])
        return open(file).read()
    except UnicodeDecodeError:
        return '[Error] Unable to read byte file'


def check_json_for_errors(widget) -> bool:
    try:
        load(open(dpg.get_value(widget)))
    except JSONDecodeError:
        return True
    return False


# block preview window
with dpg.window(width=128, height=128, no_title_bar=True, no_resize=True, no_close=True, no_move=True):
    dpg.add_text("Block preview\nwindow (BOX 1)", color=[120, 120, 120])
    # dpg.add_button(label="Save")
    # dpg.add_input_text(label="string", default_value="Quick brown fox")
    # dpg.add_slider_float(label="float", default_value=0.273, max_value=1)

# json text preview window
with dpg.window(width=662, height=274, no_title_bar=True, no_resize=True, no_close=True, no_move=True, pos=[128, 0]):
    # dpg.add_text('(BOX 2) JSON VIEWER', color=[120, 120, 120])
    text_field_widget = dpg.add_input_text(width=640, height=235, multiline=True)

    # Make file dialog
    with dpg.file_dialog(label='File Explorer', width=500, height=400, show=False, user_data=text_field_widget,
                         callback=lambda s, a, u: dpg.set_value(u, get_file_content(a)),
                         tag="__filedialog", file_count=1):
        dpg.add_file_extension('.*')

    dpg.add_button(label='Select file', user_data='__filedialog',
                   callback=lambda s, a, u: dpg.configure_item(u, show=True), pos=[402, 246])

    dpg.add_button(label='Check json for errors', pos=[490, 246], user_data=text_field_widget, callback=lambda s, a, u: check_json_for_errors(u))

# file dialog windows
with dpg.window(width=128, height=512, no_title_bar=True, no_resize=True, no_close=True, no_move=True, pos=[0, 128]):
    opened_file_in_text_field = dpg.add_text('File not selected...')

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
