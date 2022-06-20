import dearpygui.dearpygui as dpg

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=700)


def open_image(a, b):
    print(a, b)


def open_callback():
    with dpg.add_file_dialog(label="Image", callback=open_image):
        dpg.add_file_extension('Pyth{.py}')


with dpg.window(label="Example Window"):
    dpg.add_button(label="Open", callback=open_callback)

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
