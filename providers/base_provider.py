"""
IDL Live Suite
Base Provider
Version 2.0
"""


class BaseProvider:

    def __init__(self):

        self.provider_name = "Unknown"

    def connect(self):

        raise NotImplementedError

    def wait_for_match(self):

        raise NotImplementedError

    def get_match(self):

        raise NotImplementedError

    def update(self):

        raise NotImplementedError

    def close(self):

        raise NotImplementedError