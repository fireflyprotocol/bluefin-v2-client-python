import json
import aiohttp
from .interfaces import *


class APIService:
    def __init__(self, url, UUID=""):
        self.server_url = url
        self.auth_token = None
        self.api_token = None
        self.uuid = UUID
        self.client = aiohttp.ClientSession()

    async def close_session(self):
        if self.client is not None:
            return await self.client.close()

    async def get(self, service_url, query={}, auth_required=False):
        """
            Makes a GET request and returns the results
            Inputs:
                - service_url(str): the url to make the request to.
                - query(dict): the get query.
                - auth_required(bool): indicates whether authorization is required for the call or not.
        """

        url = self._create_url(service_url)

        response = None
        if auth_required:
            headers = {
                'Authorization': 'Bearer {}'.format(self.auth_token),
                'x-api-token': self.api_token or ''
            }
            if self.uuid:
                headers['x-mm-id'] = self.uuid

            response = await self.client.get(
                url,
                params=query,
                headers=headers
            )
        else:
            response = await self.client.get(url, params=query)

        try:
            if response.status != 503:  # checking for service unavailitbility
                return await response.json()
            else:
                return response
        except:
            raise Exception("Error while getting {}: {}".format(url, response))

    async def post(self, service_url, data, auth_required=False, contentType=""):
        """
            Makes a POST request and returns the results
            Inputs:
                - service_url(str): the url to make the request to.
                - data(dict): the data to post with POST request.
                - auth_required(bool): indicates whether authorization is required for the call or not.
        """
        url = self._create_url(service_url)
        response = None
        if auth_required:
            headers = {
                'Authorization': 'Bearer {}'.format(self.auth_token)
            }
            if self.uuid:
                headers['x-mm-id'] = self.uuid

            if contentType is not "":
                headers['Content-type'] = contentType

            response = await self.client.post(url=url, data=data, headers=headers)
        else:
            response = await self.client.post(url=url, data=data)

        try:
            if response.status != 503:  # checking for service unavailitbility
                return await response.json()
            else:
                return response
        except:
            raise Exception(
                "Error while posting to {}: {}".format(url, response))

    async def delete(self, service_url, data, auth_required=False):
        """
            Makes a DELETE request and returns the results
            Inputs:
                - service_url(str): the url to make the request to.
                - data(dict): the data to post with POST request.
                - auth_required(bool): indicates whether authorization is required for the call or not.
        """
        url = self._create_url(service_url)

        response = None
        if auth_required:
            headers = {
                'Authorization': 'Bearer {}'.format(self.auth_token)
            }
            if self.uuid:
                headers['x-mm-id'] = self.uuid

            response = await self.client.delete(
                url=url,
                data=data,
                headers=headers)
        else:
            response = await self.client.delete(url=url, data=data)

        try:
            return await response.json()
        except:
            raise Exception(
                "Error while posting to {}: {}".format(url, response))

    """
        Private methods
    """

    def _create_url(self, path):
        """
        Appends namespace to server url
        """
        return "{}{}".format(self.server_url, path)

    def set_uuid(self, uuid):
        self.uuid = uuid
