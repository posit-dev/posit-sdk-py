import pytest

from typing import Any, List, Optional

from posit.connect.resources import Resources


class TestResources(Resources[Any]):
    def create(self) -> Any:
        return super().create()  # type: ignore [safe-super]

    def delete(self) -> None:
        return super().delete()  # type: ignore [safe-super]

    def find(self) -> List[Any]:
        return super().find()  # type: ignore [safe-super]

    def find_one(self) -> Optional[Any]:
        return super().find_one()  # type: ignore [safe-super]

    def get(self) -> Any:
        return super().get()  # type: ignore [safe-super]

    def update(self) -> Any:
        return super().update()  # type: ignore [safe-super]

    def test_create(self):
        with pytest.raises(NotImplementedError):
            self.create()

    def test_delete(self):
        with pytest.raises(NotImplementedError):
            self.delete()

    def test_find(self):
        with pytest.raises(NotImplementedError):
            self.find()

    def test_find_one(self):
        with pytest.raises(NotImplementedError):
            self.find_one()

    def test_get(self):
        with pytest.raises(NotImplementedError):
            self.get()

    def test_update(self):
        with pytest.raises(NotImplementedError):
            self.update()
