import dearpygui.dearpygui as dpg
from dearpygui import demo

dpg.create_context()
dpg.create_viewport(title='Custom Title', width=800, height=700)

demo.show_demo()

dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
