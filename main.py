from json import loads, dump, load, JSONDecodeError
from subprocess import Popen
from os.path import getsize, exists, split
from os import getenv, remove
from random import getrandbits
from datetime import datetime
import dearpygui.dearpygui as dpg
from PIL import Image

__version__ = 'b22.08.2022a'
SUBLIME_TEXT_PATH = 'C:\\Program Files\\Sublime Text\\sublime_text.exe'
NOTEPAD_PP_PATH = 'C:\\Program Files\\Notepad++\\notepad++.exe'
NOTEPAD_PATH = 'C:\\Windows\\notepad.exe'
SETTINGS_FILENAME = 'settings.json'
TMP = getenv('tmp')

# load the settings, if error create the new one
try:
    SETTINGS: dict = load(open(SETTINGS_FILENAME))
    SETTINGS.get('last_used_path')
except BaseException:
    SETTINGS = {'last_used_path': ''}
    dump(SETTINGS, open(SETTINGS_FILENAME, 'w'))

# create a main window
dpg.create_context()
dpg.create_viewport(title=f'JPack Editor version {__version__}', width=800, height=700, resizable=False)
dpg.set_viewport_small_icon('Icon.ico')


def to_fixed(num_obj: float, digits=0) -> float:
    return float(f'{num_obj:.{digits}f}')


def get_rand_hash() -> str:
    return '%016x' % getrandbits(64)


def __write_field(text: str, field: str):
    if field == 'program_logs':
        current_time = datetime.now().strftime("%Y.%m.%d %H:%M:%S")
        dpg.set_value('program_logs', f'{dpg.get_value("program_logs")}[{current_time}]{text}\n')
    else:
        dpg.set_value(field, text)


def __load_file(dpg_info: dict):
    # get path and name of the file
    filename, path = list(dpg_info['selections'].items())[0]

    # save the last used path to settings
    SETTINGS['last_used_path'] = split(path)[0]
    dump(SETTINGS, open(SETTINGS_FILENAME, 'w'))

    # load the contents of the file, if there is an error print it out in the log
    try:
        __write_field(open(path).read(), 'json_field')
    except BaseException:
        __write_field('[ERROR]: Unable to read the file', 'program_logs')

    # collect the file info
    filename, path = list(dpg_info['selections'].items())[0]
    size = getsize(path) / 1024  # weight in kilobytes

    # if the file size if more than 900 kb, convert the size to mb
    if size > 900:  # if size is more than 900 kb
        size = to_fixed(size / 1024, 4)  # weight in mb (rounded to 4 numbers after comma)
        size = f'{size} (MB)'
    else:
        size = to_fixed(size, 4)  # weight in kb (rounded to 4 numbers after comma)
        size = f'{size} (KB)'

    dpg.set_value('file_name_obj', f'\tName: {filename}')
    dpg.set_value('file_path_obj', f'\tPath: {path}')
    dpg.set_value('file_size_obj', f'\tSize: {size}')

    # change textures in box 1 (block preview)
    # detecting the textures mention
    try:
        file_content: dict = loads(open(path).read()).get('textures')
    except BaseException:
        __write_field('[ERROR]: Failed to load the json content', 'program_logs')
    else:
        textures_paths = list(file_content.values())
        textures_paths = [f'{i}.png' for i in list(set(textures_paths))]  # deleting duplicates and adding ".png" to the end
        # define the texture partition (minecraft/optifine etc.) (assets/PARTITION/textures/...)
        try:
            tp_root: list = path.replace('\\', '/').split('/')  # '...', '...', '...', 'resourcepacks', 'RP_NAME', '...'
            tp_root: list = tp_root[:tp_root.index('resourcepacks') + 2]  # ['...', 'resourcepacks', 'RP_NAME']
            tp_root: str = '/'.join(list(tp_root))
        except BaseException:
            __write_field("[ERROR]: Unable to define texture paths (json not in resourcepack's folder)\n", 'program_logs')
        else:

            # get full paths of the textures
            out_textures_paths = []
            for texture in textures_paths:
                texture = texture.split(':')  # if exists, texture = ['PARTITION', 'block|item/...'], if not texture = ['block|item/...']
                if len(texture) == 1:  # if len(texture) == len(['block|item/...'])
                    out_textures_paths.append(f'{tp_root}/assets/minecraft/textures/{texture[0]}')
                else:
                    out_textures_paths.append(f'{tp_root}/assets/{texture[0]}/textures/{texture[1]}')

            # textures paths collected, now display only existing textures
            # open and compress the texture to 16x16 (if the texture is larger, it will fit in the window)
            resized_textures = []
            try:
                for texture in out_textures_paths:
                    texture = Image.open(texture).resize((32, 32), Image.NEAREST)
                    resized_name = f'{TMP}/{get_rand_hash()}.png'
                    texture.save(resized_name, bitmap_format='png')

                    resized_textures.append(resized_name)
            except BaseException as err:
                __write_field('[ERROR]: Failed to open textures from json\n'
                              f'({err})', 'program_logs')

            # load the resized textures
            loaded = []
            try:
                for texture in resized_textures:
                    width, height, channels, data = dpg.load_image(texture)

                    with dpg.texture_registry():
                        loaded.append(dpg.add_static_texture(width, height, data))

                    remove(texture)
            except BaseException as err:
                __write_field('[ERROR]: Failed to load textures from temp folder\n'
                              f'({err})', 'program_logs')

            # show the loaded textures
            with dpg.window(width=128, height=128, no_title_bar=True, no_resize=True, no_close=True, no_move=True):
                x, y = [0, 0]
                for i in loaded:
                    if x == 4:
                        x, y = [0, y + 1]
                    space = 3 + 13 * x if x != 0 else 3  # 3, because if a texture is near a window border, it is clipped, 13 * x is the pixel distance between textures
                    dpg.add_image(i, pos=[x * 32 + space, y * 32])
                    x += 1


def __check_json_for_errors():
    try:
        loads(dpg.get_value('json_field'))
        __write_field('[INFO]: File successfully checked', 'program_logs')
    except JSONDecodeError as error:
        __write_field(f'[ERROR]: {error}', 'program_logs')


def __clear_field(obj: str):
    dpg.set_value(obj, '')


def __open_in_external_editor(collect_field: str):
    file_path = dpg.get_value(collect_field)[7:]  # remove "Path: " text in the start
    for editor in [SUBLIME_TEXT_PATH, NOTEPAD_PP_PATH, NOTEPAD_PATH]:
        if exists(editor):
            Popen(f'"{editor}" "{file_path}"')
            __write_field('[INFO]: Opened json in external editor', 'program_logs')
            break


def __open_file_folder():
    try:
        file_path = dpg.get_value('file_path_obj')[7:]  # '.../.../FILE'
        file_path = file_path.replace('\\', '/').split('/')[:-1]  # ['...', '...']
        file_path = '\\'.join(file_path)  # '...\...'

        Popen(f'explorer "{file_path}"')
        __write_field('[INFO]: Opened file folder', 'program_logs')
    except BaseException:
        __write_field('[ERROR]: Unable to open file folder', 'program_logs')


def __open_rp_folder():
    try:
        file_path: str = dpg.get_value('file_path_obj')[7:]  # '.../.../FILE'
        file_path: list = file_path.replace('\\', '/').split('/')[:-1]  # ['...', '...', 'resourcepacks', 'RP_NAME', '...']
        file_path = file_path[:file_path.index('resourcepacks') + 2]  # ['...', '...', 'resourcepacks', 'RP_NAME']
        file_path: str = '\\'.join(file_path)  # '...\...\resourcepacks\RP_NAME'

        Popen(f'explorer "{file_path}"')
        __write_field('[INFO]: Opened resourcepack folder', 'program_logs')
    except BaseException:
        __write_field('[ERROR]: Unable to open resourcepack folder', 'program_logs')


# block preview window
with dpg.window(width=128, height=128, no_title_bar=True, no_resize=True, no_close=True, no_move=True):
    dpg.add_text('Texture previews\n'
                 'will be here')

# json text preview window
with dpg.window(width=662, height=274, no_title_bar=True, no_resize=True, no_close=True, no_move=True, pos=[128, 0]):
    # json text field
    dpg.add_input_text(width=640, height=235, multiline=True, tag='json_field')

    # register a file dialog
    with dpg.file_dialog(label='File Explorer', width=500, height=400, show=False, user_data='json_field',
                         callback=lambda s, a, u: __load_file(a), tag='__filedialog', file_count=1,
                         default_path=f'{SETTINGS["last_used_path"]}\\'):
        dpg.add_file_extension('.*')

    dpg.add_button(label='Select file', user_data='__filedialog', callback=lambda s, a, u: dpg.configure_item(u, show=True), pos=[7, 246])
    dpg.add_button(label='Open rp folder', callback=lambda s, a, u: __open_rp_folder(), pos=[94, 246])
    dpg.add_button(label='Open file folder', callback=lambda s, a, u: __open_file_folder(), pos=[202, 246])
    dpg.add_button(label='Open in external editor', callback=lambda s, a, u: __open_in_external_editor('file_path_obj'), pos=[324, 246])
    dpg.add_button(label='Check json for errors', pos=[495, 246], callback=__check_json_for_errors)

# information window
with dpg.window(width=662, height=128, no_title_bar=True, no_resize=True, no_close=True, no_move=True, pos=[128, 274]):
    # Opened file info
    dpg.add_text('File info:')
    dpg.add_text(tag='file_name_obj')
    dpg.add_text(tag='file_path_obj')
    dpg.add_text(tag='file_size_obj')

# error window
with dpg.window(width=672, height=259, no_title_bar=True, no_resize=True, no_close=True, no_move=True, pos=[128, 402]):
    dpg.add_text('Program logs:')
    dpg.add_input_text(multiline=True, readonly=True, width=640, height=215, tag='program_logs')
    dpg.add_button(label='Clear logs', user_data='program_logs', callback=lambda s, a, u: __clear_field(u), pos=[569, 9])


# Start the dpg
dpg.setup_dearpygui()
dpg.show_viewport()
dpg.start_dearpygui()
dpg.destroy_context()
