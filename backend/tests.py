from unittest.mock import Mock, patch
import pytest
from models.events import EventModel


def test_get_events_today():
    response = EventModel.get_mocked_events()
    assert len(response["events"]) == 2