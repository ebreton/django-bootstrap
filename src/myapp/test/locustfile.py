from locust import HttpLocust, TaskSet, task


def increment():
    increment.i += 1
    return increment.i


increment.i = 0


class Scenario1(TaskSet):
    @task(2)
    def create_greeting(self):
        response = self.client.get("/greetings/new/")
        csrftoken = response.cookies.get('csrftoken')
        self.client.post("/greetings/new/",
                         {"name": "Test%s" % increment(),
                          "csrfmiddlewaretoken": csrftoken}
                         )

    @task(60)
    def list_greetings(self):
        self.client.get("/greetings/")


class WebsiteUser(HttpLocust):
    host = "http://127.0.0.1:8000"
    task_set = Scenario1
    min_wait = 1000
    max_wait = 1000
