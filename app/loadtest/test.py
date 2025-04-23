from locust import HttpUser, task, between
import random

class AuthUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://localhost:5000"  # Update with your app's URL

    def on_start(self):
        self.username = f"loaduser{random.randint(1, 1000000)}"
        self.password = "testpass123"
        
        # Register user
        self.client.post("/register", data={
            "username": self.username,
            "password": self.password
        })
        
        # Login and store cookies
        response = self.client.post("/login", data={
            "username": self.username,
            "password": self.password
        })
        self.cookies = response.cookies

    @task(3)
    def shorten_url(self):
        """Test URL shortening flow"""
        # Get CSRF token from index page
        response = self.client.get("/")
        csrf_token = response.cookies.get("csrf_access_token")
        
        self.client.post("/shorten", 
            data={"url": f"https://example.com/{random.randint(1000,9999)}"},
            cookies={"csrf_access_token": csrf_token},
            headers={"X-CSRF-TOKEN": csrf_token}
        )

    @task(1)
    def view_stats(self):
        """Test stats viewing"""
        self.client.get("/stats")


class ShorteningUser(HttpUser):
    wait_time = between(1, 5)
    
    @task(3)
    def shorten_url(self):
        # Get CSRF token from home page
        response = self.client.get("/")
        csrf_token = response.cookies.get("csrf_token")
        
        self.client.post("/shorten", 
            data={"url": f"https://example.com/{random.randint(1000,9999)}"},
            cookies={"csrf_token": csrf_token}
        )

    @task(1)
    def view_stats(self):
        self.client.get("/stats")


class RedirectUser(HttpUser):
    wait_time = between(0.1, 0.5)
    host = "http://localhost:5000"

    def on_start(self):
        # Create a test user for redirects
        self.auth_user = AuthUser(self.host)
        self.auth_user.on_start()
        self.cookies = self.auth_user.cookies
        
        # Create a test URL to click
        response = self.auth_user.client.post("/shorten", 
            data={"url": "https://example.com/load-test"},
            cookies=self.cookies
        )
        self.short_code = response.url.split("/")[-1]

    @task(10)
    def click_shortlink(self):
        # Get fresh CSRF token
        response = self.client.get("/", cookies=self.cookies)
        csrf_token = response.cookies.get("csrf_access_token")
        
        with self.client.get(f"/{self.short_code}", 
            cookies=self.cookies,
            catch_response=True
        ) as response:
            if response.status_code != 302:
                response.failure(f"Unexpected status: {response.status_code}")
