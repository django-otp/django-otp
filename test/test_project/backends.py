from __future__ import absolute_import, division, print_function, unicode_literals


class DummyBackend(object):
    def authenticate(self, request):
        return None

    def get_user(self, user_id):
        return None
