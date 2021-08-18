from ..utils import RESOURCES_DIR

class TestUtils:

    def test_resources_exist(self):
        import os
        assert os.path.exists(RESOURCES_DIR)