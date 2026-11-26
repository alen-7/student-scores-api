"""Test setup: fixed test login, and a clean store before every test."""

import os

os.environ["API_USERNAME"] = "teacher"
os.environ["API_PASSWORD"] = "test-password"

import pytest  # noqa: E402

import store  # noqa: E402


@pytest.fixture(autouse=True)
def clean_store():
    store.reset()
    yield
    store.reset()
