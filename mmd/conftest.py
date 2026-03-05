# conftest.py (nella root del progetto)
import django
import pytest

@pytest.fixture
def rf():
    from django.test import RequestFactory
    return RequestFactory()