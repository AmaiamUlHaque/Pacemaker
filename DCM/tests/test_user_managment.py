import os
import pytest
from core import user_management

TEST_USER_FILE = os.path.join(os.path.dirname(__file__), "test_users.json")
user_management.USER_FILE = TEST_USER_FILE #override default file

@pytest.fixture(autouse=True)
def clear_file():
    """Reset users.json after each test"""
    user_management.reset_users()
    yield
    if os.path.exists(TEST_USER_FILE):
        os.remove(TEST_USER_FILE)

def test_register_and_autheticate():
    assert user_management.register_user("diego", "abc") is True
    assert user_management.authenticate_user("diego", "abc") is True
    assert user_management.register_user("diego", "123") is False
    assert user_management.authenticate_user("diego", "124") is False
    assert user_management.authenticate_user ("bob", "123") is False

def test_MAX_USER_LIMIT():
    for i in range(user_management.MAX_USERS):
        assert user_management.register_user(f"user{i}", "pass") is True
    assert user_management.register_user("11", "pass") is False #11 user should fail
    
def test_list_and_remove_user():
    user_management.register_user("charlie", "123")
    assert "charlie" in user_management.list_users()

    assert user_management.remove_user("charlie") is True
    assert "charlie" not in user_management.list_users()

    # removing again should fail
    assert user_management.remove_user("charlie") is False


def test_reset_users():
    user_management.register_user("temp", "pw")
    assert "temp" in user_management.list_users()

    user_management.reset_users()
    assert user_management.list_users() == []