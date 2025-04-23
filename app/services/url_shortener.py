import string,random

class URLShortener:
    def __init__(self, storage, code_length=6):
        self.storage = storage
        self.code_length = code_length
        self.characters = string.ascii_letters + string.digits

    def generate_short_code(self):
        while True:
            code = ''.join(random.choices(self.characters, k=self.code_length))
            if not self.storage.code_exists(code):
                return code
    
    def shorten_url(self, original_url, user_id):
        short_code = self.generate_short_code()
        self.storage.save_url(short_code, original_url, user_id)
        return short_code
    
    def get_original_url(self, short_code):
        return self.storage.get_url(short_code)

