from environs import Env

env = Env()
env.read_env()

BOT_TOKEN = env.str("BOT_TOKEN")
ADMIN = env.str("ADMIN")

DB_USER = env.str("DATABASE_ROOT_USERNAME")
DB_PSSWD = env.str("DATABASE_ROOT_PASSWORD")
HOST = env.str("DB_HOST")
DB_NAME = env.str("DB_NAME")

