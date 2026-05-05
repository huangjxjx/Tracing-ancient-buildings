import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_application


@pytest.fixture()
def client() -> TestClient:
    app = create_application()
    with TestClient(app) as test_client:
        yield test_client
