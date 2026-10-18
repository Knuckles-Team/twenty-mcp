import pytest


@pytest.fixture
def mock_ctx():
    class MockCtx:
        def info(self, msg):  # noqa: V107
            return None

        def warn(self, msg):  # noqa: V107
            return None

        def error(self, msg):  # noqa: V107
            return None

    return MockCtx()
