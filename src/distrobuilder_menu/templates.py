""" Template functions to manipulate LXD JSON data
"""
from datetime import datetime, timedelta
from pathlib import Path
import platform
from pprint import pprint
import subprocess
# app modules
from distrobuilder_menu import utils
# app classes
from distrobuilder_menu.config.app import AppConfig
from distrobuilder_menu.config.user import Settings
from distrobuilder_menu.api.gethub import Gethub
from distrobuilder_menu.api.spinner import Spinner

# globals
# singleton class shares user config between modules
USER_CONFIG = Settings.instance()
# singleton class for Github API methods
GETHUB = Gethub.instance()
# read command line
# ARGS are global to query building LXC or LXD images
ARGS = AppConfig.instance()
DEBUG_TIMER = utils.Timer(ARGS.timer)


def get_user_config():
    """ Displays & optionally edits User Settings
    """
    print('\nDistrobuilder Menu settings:\n')

    # accessing the __dict__ attribute is faster than vars()
    # https://www.pythondoeswhat.com/2012/01/dict-and-vars.html
    pprint(USER_CONFIG.__dict__)
    print(f"\nUser Configuration: {USER_CONFIG.dbmenu_config}")

    # edit configuration
    question='\nEdit configuration [Y/n]: ? '
    utils.edit_file(USER_CONFIG.dbmenu_config, USER_CONFIG.console_editor, question=question)

    # re-read configuration
    print(f"Reloading: {USER_CONFIG.dbmenu_config}")
    Settings.instance()


def update_lxd_json():
    """ Refreshes JSON data from LXD.
        the file age check remains in load_json_cache() so the JSON
        data can be force updated if needed.
    """
    msg = f"\nUpdating LXD version data: {USER_CONFIG.lxd_json} ..."
    command = f"lxc image ls -f json images: > {USER_CONFIG.lxd_json}"
    json_file = Path(USER_CONFIG.lxd_json)
    output_dir = json_file.parent

    # ensure destination folder exists
    if not output_dir.is_dir():
        try:
            output_dir.mkdir(parents=True)
        # cross platform & also catches permission errors
        except (OSError, IOError) as err:
            utils.die(1, f"Error: {err.args[1]} : {output_dir}")

    try:
        # nice simple activity indicator
        with Spinner(msg):
            retval = subprocess.check_output(command, shell=True, text=True)
    except subprocess.CalledProcessError as err:
        utils.die(1, f"Updating failed with error: {err.returncode}")

    if retval == '':
        # update cache
        lxd_json = utils.read_config(USER_CONFIG.lxd_json, ARGS.timer)
        json_data = process_data(lxd_json)
        cache_to_json(json_data, USER_CONFIG.json_cachefile)
        # keep templates in sync
        update_templates()


def cache_to_json(data, outfile):
    """ Used to cache dictionary data from process_data() to json.
        LXD json typically doesn't change often so cache the data
        (JSON from LXD is 2mb versus 28kb of data we need) - cPickle
        serialises faster but is a security risk. JSON is fast enough.
    """
    print(f"\nCaching JSON data to: {outfile}")
    utils.write_config(outfile, data, data_type='json', enabled=ARGS.timer)


def load_json_cache():
    """ Reading LXD_JSON takes 0.65 sec versus 0.0083 sec
        with a cached version containing just the data we need
        (which changes infrequently & is automatically updated here weekly)
    """
    DEBUG_TIMER.start()

    one_week_ago = datetime.now() - timedelta(days=7)
    json_file = Path(USER_CONFIG.lxd_json)

    # on new installs no json cache exists yet
    if json_file.is_file():
        filetime = datetime.fromtimestamp(json_file.stat().st_mtime)
    else:
        # so trigger an update
        filetime = datetime.now() - timedelta(days=8)

    if filetime < one_week_ago:
        print('\nJSON data is over 1 week old.')

        # also runs main computation: process_data() & caches json
        update_lxd_json()

        # queries the Github API for updates
        update_templates()

    json_data = utils.read_config(USER_CONFIG.json_cachefile, ARGS.timer)

    DEBUG_TIMER.stop(post_msg=USER_CONFIG.json_cachefile)
    return json_data


def update_templates():
    """ Checks the local template sizes against the list of dicts returned
        by custom class method Gethub.check_file_list()
        Finally passes a list of url's to Gethub.download_files()
    """
    download_list = []
    # lxc/lxc-ci/images API endpoint
    url = f"{GETHUB.api_contents}/images"

    # check the Github 'contents' API
    file_list = GETHUB.check_file_list(url)

    # compare local / remote file sizes
    for remote_file in file_list:
        local_file = Path(f"{USER_CONFIG.subdir_images}/{remote_file['name']}")

        if Path(local_file).is_file():
            local_file_size = Path(local_file).stat().st_size
        else:
            local_file_size = 0

        if local_file_size != remote_file['size']:
            file_dict = {}
            file_dict['url'] = remote_file['download_url']
            file_dict['file'] = local_file
            download_list.append(file_dict)

    # download files
    if download_list:
        GETHUB.download_files(download_list)
    else:
        utils.die(0, f"Template files are up to date: {USER_CONFIG.subdir_images}\n")


def process_data(lxd_json_data):
    """Parses LXD json data & Returns a list of dicts with
       relevant template build options.

       Used by menu_versions() to display build options.
    """
    DEBUG_TIMER.start()
    build_option_list = []

    # sanity checks
    if len(lxd_json_data) == 0:
        utils.die(1, 'Error: empty dictionary passed to process_data()')

    # ARGS.lxd is usually True so check ARGS.lxc
    if ARGS.lxc:
        disk_list = 'squashfs'
    else:
        disk_list = ('squashfs', 'disk-kvm.img')

    # returns x86_64 (uname values)
    platform_machine = platform.machine()

    for item in lxd_json_data:

        # empty dict
        item_dict = {}

        # distrobuilder does not cross build so only
        # generate build options for the host system (e.g x86_64)
        arch_top_level = item['architecture']

        if arch_top_level == platform_machine:

            aliases = item['aliases']

            # aliased entries of type squashfs / disk-kvm.img are unique
            if aliases is not None:

                # read initial properties for 2nd condition
                properties = item['properties']
                item_type = properties['type']

                # non metadata entries are unique
                if item_type in (disk_list):

                    # finish reading item properties
                    item_dict['arch_top_level'] = item['architecture']

                    # container or virtual-machine
                    item_dict['type_top_level'] = item['type']

                    # template filenames are lower case see find_files()
                    item_dict['os'] = properties['os'].lower()
                    item_dict['type'] = properties['type']
                    item_dict['arch'] = properties['architecture']
                    item_dict['release'] = properties['release']
                    item_dict['variant'] = properties['variant']

                    # add to list (append is fast)
                    build_option_list.append(item_dict)

    DEBUG_TIMER.stop()
    return build_option_list
