import os


def find_env_file(env) -> str:
    if env == "production":
        env_file = ".env.production"
    elif env == "docker":
        env_file = ".env.docker"
    else:
        env_file = ".env.development"

    return env_file


def find_env_file_full(env) -> str:
    env_file = find_env_file(env)
    return os.path.join(os.getcwd(), env_file)
