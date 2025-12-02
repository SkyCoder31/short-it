from locust import HttpUser, constant, task, between

class WebsiteUser(HttpUser):
    # Waiting between 1 and 2 seconds between tasks
    wait_time = constant(0)

    # The stress-test of the short link
    @task
    def visit_short_link(self):
        # Make sure you have created a short link with custom_key="wiki" first!
        self.client.get("/fast")