from posit.connect.metrics.rename_params import rename_params


class TestRenameParams:
    def test_start_to_from(self):
        params = {"start": ...}
        params = rename_params(params)
        assert "start" not in params
        assert "from" in params

    def test_end_to_to(self):
        params = {"end": ...}
        params = rename_params(params)
        assert "end" not in params
        assert "to" in params
