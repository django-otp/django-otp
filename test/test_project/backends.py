class DummyBackend:
    def authenticate(self, request):
        return None

    def get_user(self, user_id):
        return None
