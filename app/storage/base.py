from abc import ABC, abstractmethod

class URLStorage(ABC):
    @abstractmethod
    def save_url(self, short_code, original_url, user_id):
        pass
    
    @abstractmethod
    def get_url(self, short_code):
        pass
    
    @abstractmethod
    def code_exists(self, short_code):
        pass

    @abstractmethod
    def record_click(self, short_code, click_data):
        pass

    @abstractmethod
    def get_urls_by_user(self, user_id):
        pass