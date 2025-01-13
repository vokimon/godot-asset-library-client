import requests

class Api:
    """Access to the Godot Asset Library API"""

    def __init__(self, base=None):
        self.base = base or f"https://godotengine.org/asset-library/api/"

    def login(self, username, password):
        r = self.post('/login', json=dict(
            username=username,
            password=password,
        ))
        self.token = r['token']

    def _process_response(self, response):
        print(response.text)
        response.raise_for_status()
        try:
            return response.json()
        except:
            print(response.text)
            raise

    def post(self, url, json={}, *args, **kwds):
        if hasattr(self, 'token'):
            json = dict(json, token=self.token)

        response = requests.post(
            self.base+url,
            json=json,
            headers = {'Content-Type': 'application/json; charset=utf-8'},
            *args, **kwds)
        return self._process_response(response)

    def get(self, url, *args, **kwds):
        response = requests.get(
            self.base+url,
            *args, **kwds)
        return self._process_response(response)

    def pending_version_edit(self, asset_id, version_string):
        """
        Returns the last pending edit for the current version or None.
        """
        result = self.get('asset/edit', params=dict(
            asset=asset_id,
            status='new',
            version_string=version_string,
        ))

        edit_ids = [
            p['edit_id']
            for p in result.get('result')
            if p['version_string'] == version_string
        ]
        if edit_ids:
            return max(edit_ids)

    def asset_previews(self, asset_id):
        result = self.get(f'asset/{asset_id}')
        return result.get('previews', [])

    def asset_edit_previews(self, edit_id):
        result = self.get(f'asset/edit/{edit_id}')
        return result.get('previews', [])

