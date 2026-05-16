from __future__ import annotations

import pytest


class JsonResponse:
    def __init__(self, payload, status_code=200, content=b"", text=""):
        self.payload = payload
        self.status_code = status_code
        self.content = content
        self.text = text

    def json(self):
        return self.payload


class FakeSeries:
    def __init__(self, values):
        self.values = values

    def dropna(self):
        return self

    def unique(self):
        return list(dict.fromkeys(value for value in self.values if value is not None))

    def __eq__(self, other):
        return [value == other for value in self.values]


class FakeDataFrame:
    def __init__(self, rows=None, columns=None):
        self.rows = rows or []
        self.columns = columns or list(self.rows[0].keys()) if self.rows else columns or []
        self.empty = not self.rows

    def __contains__(self, item):
        return item in self.columns

    def __getitem__(self, key):
        if isinstance(key, str):
            return FakeSeries([row.get(key) for row in self.rows])
        return FakeDataFrame([row for row, keep in zip(self.rows, key) if keep], columns=self.columns)

    def iterrows(self):
        for index, row in enumerate(self.rows):
            yield index, row

    def head(self, n):
        return FakeDataFrame(self.rows[:n], columns=self.columns)


@pytest.fixture
def sample_quote_line():
    vals = [""] * 88
    vals[1] = "绿的谐波"
    vals[2] = "688017"
    vals[3] = "305.50"
    vals[4] = "265.00"
    vals[5] = "265.50"
    vals[31] = "40.50"
    vals[32] = "15.28"
    vals[33] = "315.00"
    vals[34] = "262.00"
    vals[37] = "584581"
    vals[38] = "10.98"
    vals[39] = "409.55"
    vals[43] = "20.00"
    vals[44] = "560.07"
    vals[45] = "560.07"
    vals[46] = "15.69"
    vals[47] = "318.00"
    vals[48] = "212.00"
    vals[49] = "1.20"
    vals[52] = "420.00"
    return 'v_sh688017="' + "~".join(vals) + '";'


@pytest.fixture
def forecast_df():
    return FakeDataFrame([
        {"年度": "2026", "均值": 3.0, "预测机构数": 5},
        {"年度": "2027", "均值": 4.5, "预测机构数": 5},
    ])
