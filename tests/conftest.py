import os

import pytest


if not os.getenv("TEST_DATABASE_URL"):
    pytest.skip("TEST_DATABASE_URL is required; tests never use SQLite or the development database", allow_module_level=True)
