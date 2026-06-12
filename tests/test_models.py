from loguru import logger

from banana_netcraze.models.device import DeviceDhcpModel


def test_extra_fields_are_saved_and_warned_about():
    messages = []
    sink_id = logger.add(messages.append, format="{message}")

    try:
        model = DeviceDhcpModel(expires=60, lease_type="dynamic", renew_count=2)
    finally:
        logger.remove(sink_id)

    assert model.extra_fields == {"lease_type": "dynamic", "renew_count": 2}
    assert len(messages) == 1
    assert (
        "Unexpected fields in DeviceDhcpModel: lease_type (str), renew_count (int)."
        in messages[0]
    )
    assert "https://github.com/BananaLoaf/banana-netcraze/issues" in messages[0]
