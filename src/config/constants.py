import os

# this should be the only place where the environment is defined
ENV = os.getenv("ENV", "development")
