from app.storage.base import URLStorage

class InMemoryURLStorage(URLStorage):
    def __init__(self):
        self.urls = {}
        
    def save_url(self, short_code, original_url, user_id):
        self.urls[short_code] = {
            'original_url': original_url,
            'user_id': user_id,
            'clicks': []
        }
        
    def get_url(self, short_code):
        entry = self.urls.get(short_code)
        return entry['original_url'] if entry else None
    
    def code_exists(self, short_code):
        return short_code in self.urls

    def record_click(self, short_code, click_data):
        if short_code in self.urls:
            self.urls[short_code]['clicks'].append(click_data)

    def get_urls_by_user(self, user_id):
        user_urls = []
        for code, data in self.urls.items():
            if data['user_id'] == user_id:
                user_urls.append({
                    'short_code': code,
                    'original_url': data['original_url'],
                    'clicks': data['clicks']
                })
        return user_urls