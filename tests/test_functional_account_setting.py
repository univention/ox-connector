import pytest
from contextlib import nullcontext as does_not_raise

from univention.ox.provisioning.functional_account import configure_functional_account_login, InvalidSetting


@pytest.mark.parametrize("test_input,expected_output,expectation",
                         [("{{fa_entry_uuid}}", [(0, 17)], does_not_raise()),
                          ("{{entry_uuid}}{{fa_entry_uuid}}", [
                           (14, 31), (0, 14)], does_not_raise()),
                          ("{{fa_entry_uuid}}:", [(0, 17)], does_not_raise()),
                          ("{{fa_entry_uuid}}::::", [
                           (0, 17)], does_not_raise()),
                          ("{{fa_entry_uuid}}:{{username}}", [
                           (18, 30), (0, 17)], does_not_raise()),
                          ("{{fa_entry_uuid}}:{{username}}+",
                           [(18, 30), (0, 17)], does_not_raise()),
                          (".{{fa_entry_uuid}}", [(1, 18)], does_not_raise()),
                          ("{{fa_entry_uuid}}a", [(0, 17)], does_not_raise()),
                          ("fa_entry_uuid", [], does_not_raise()),
                          ])
def test_funcitonal_account_setting(test_input, expected_output, expectation):
    with expectation:
        res = configure_functional_account_login(test_input)
        assert res == expected_output
