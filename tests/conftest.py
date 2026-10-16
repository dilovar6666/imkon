import os

os.environ["DATABASE_URL"] = os.getenv(
    "TEST_DATABASE_URL", "postgresql+psycopg://imkon_test:unused@127.0.0.1:5432/imkon_test"
)
os.environ.setdefault("JWT_SECRET_KEY", "test-only-secret-key-with-at-least-32-characters")
