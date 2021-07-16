## pip install locust
## locust --host=https://csbi.chalmers.se

import time
from locust import HttpUser, task, between

class RandomUser(HttpUser):
    wait_time = between(1, 10)

    @task(1)
    def index(self):
        self.client.get("/api/v2/repository/integrated_models/")

    @task(2)
    def explore(self):
        self.client.get("/api/v2/1_3_0/random-components?model=HumanGem")

    @task(3)
    def explore(self):
        self.client.get("/api/v2/1_3_0/reactions/HMR_8313")
        self.client.get("/api/v2/1_3_0/reactions/HMR_8313/related-reactions")

    @task(4)
    def browserR(self):
        self.client.get("/api/v2/1_3_0/subsystems/transport_reactions")
        self.client.get("/api/v2/1_3_0/subsystems/transport_reactions/related-reactions?limit=200")

    @task(5)
    def browserM(self):
        self.client.get("/api/v2/1_3_0/metabolites/m00010s")
        self.client.get("/api/v2/1_3_0/metabolites/m00010s/related-metabolites")

    @task(6)
    def viewer(self):
        self.client.get("/api/v2/1_3_0/maps/listing")
        self.client.get("/api/v2/rna/all")
        self.client.get("/api/v2/svg/Human-GEM/cytosol_1.svg")

    def on_start(self):
        self.client.get("/")