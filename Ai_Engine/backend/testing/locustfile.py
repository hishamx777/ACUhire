from locust import HttpUser, task, between

class CVApiTester(HttpUser):
    wait_time = between(1, 3) 

    @task(1)
    def check_health(self):
        self.client.get("/health")

    @task(3)
    def ask_cv_question(self):

        payload = {"question": "What are the programming and machine learning skills of this candidate?"}
        self.client.post("/ask", json=payload)