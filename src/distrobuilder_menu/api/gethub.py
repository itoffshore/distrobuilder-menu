""" A class to retrieve Github folders / files
"""
import json
from pathlib import Path
import shutil
from urllib.parse import urlparse
import urllib3
# app modules
from distrobuilder_menu import utils
# app classes
from distrobuilder_menu.api.singleton import SingletonThreadSafe
from distrobuilder_menu.config.user import Settings

class Gethub(SingletonThreadSafe):
    """ Another singleton class to ensure Github API calls are made
        efficiently using urllib3 Connection Pooling (as most folder
        downloads will probably be unauthenticated)
    """
    def __init__(self):

        # fix pyint 'super-init-not-called'
        super().__init__()

        # read user settings (Settings is also a singleton)
        user_config = Settings.instance()
        base_url = user_config.gh_api_url

        # fixed API endpoints
        self.api_rate = f"{base_url}/rate_limit"

        # build API urls for use with dbmenu
        if user_config.gh_owner and user_config.gh_repo:
            self.repos = f"{base_url}/repos/{user_config.gh_owner}/{user_config.gh_repo}"
            self.api_contents = f"{self.repos}/contents"
            self.api_commits = f"{self.repos}/commits"

        # add Access Token if configured
        self.token = user_config.github_token

        if self.token:
            # f-strings don't work here
            self.headers = {'Accept': 'application/vnd.github+json',
                            'Authorization': ' '.join(['token', self.token]) }
        else:
            self.headers = {'Accept': 'application/vnd.github+json'}

        # create HTTP session pool
        self.http = urllib3.PoolManager()


    # https://stackoverflow.com/a/17626704/555451
    def call_the_api(self, http_type, url, data_type='json'):
        """ Dedicated function for HTTP error handling in a single place.
            Returns either a decoded JSON data object or a binary download
            Nowadays urllib3 by default has set in responses 'auto_close': True
            (so no need to manually close the connection as still shown in the docs)
        """
        #print(f"\nDEBUG: call_the_api()\n\n {http_type} {self.headers}\n {url}\n")
        if data_type == 'json':
            print(f"\nQuerying the Github REST API: {url}")

        try:
            # validate the url (prevents a chain of errors)
            if self.check_url(url):

                if data_type == 'json':
                    response = self.http.request(http_type, url, headers=self.headers)
                    try:
                        data = json.loads(response.data)
                        # Github API returns messages not HTTP errors on invalid urls
                        if 'message' in data:
                            utils.die(1, f"Error: {data['message']} {http_type} {url}")
                    except json.decoder.JSONDecodeError:
                        utils.die(1, 'Error in query: no JSON Data was returned')
                else:
                    # no headers sent for downloads
                    # 'preload_content = False' is recommended for downloading large files
                    data = self.http.request(http_type, url, preload_content=False)
            else:
                # bad url given
                utils.die(1, f"Error: malformed url: {url}")

        # rarely reached as the Github API returns 'message' key on errors
        # HTTPError is the Base exception for urllib3 so should catch everything
        except urllib3.exceptions.NewConnectionError as err:
            utils.die(1, f"Connection Error: {err.args[1]}")
        except urllib3.exceptions.HTTPError as err:
            utils.die(1, f"HTTP error:' {err.args[1]}")

        return data


    def check_rate_limit(self):
        """ Queries the Github Rate Limit API & prints current limits
            NB: 'rate' key is being deprecated in favor of 'core'
        """
        data = self.call_the_api('GET', self.api_rate)
        print(data['resources']['core'])


    def check_file_list(self, url):
        """ Extracts just the data we need from Github's API JSON & returns
            a list of dicts with only keys: name / size / download_url
            called by update_templates() but can be used by anything.
        """
        data = self.call_the_api('GET', url)
        file_list = []

        for link in data:
            file_dict = {}
            file_dict['name'] = link['name']
            file_dict['size'] = link['size']
            file_dict['download_url'] = link['download_url']

            file_list.append(file_dict)

        return file_list


    def check_url(self, url):
        """ convenience function for validating URL's
            used by call_the_api() to prevent a cascade of errors
        """
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except ValueError:
            return False


    def download_files(self, file_dict):
        """ As input takes a list of dicts with keys: 'url' / 'file' as the
            source & destination of file downloads. Input is generated by
            update_templates() in the main application.
        """
        for item in file_dict:
            url = item['url']
            file = item['file']

            print(f"\nDownloading:\n {url}")

            # check destination folder exists
            dest_dir = Path(file).parent

            if not dest_dir.is_dir():
                choice = utils.get_input(f"\nCreate destination ? : {dest_dir} [y/N] ",
                                            accept_empty=True
                                        )
                # create destination
                if choice.startswith('y') or choice.startswith('Y'):
                    try:
                        dest_dir.mkdir(parents=True)
                    # cross platform & also catches permission errors
                    except (OSError, IOError) as err:
                        utils.die(1, f"Error: {err.args[1]} : {dest_dir}")
                else:
                    utils.die(1, f"Cancelled download of: {file}\n")

            # download the file
            with open(file, 'wb') as out_file:
                response = self.call_the_api('GET', url, data_type = 'binary')
                shutil.copyfileobj(response, out_file)
                print(f" Saved to: ==> {file}")
