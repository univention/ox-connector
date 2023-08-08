import pytest
from contextlib import nullcontext as does_not_raise

from univention.ox.provisioning.functional_account import configure_functional_account_login, InvalidSetting


@pytest.mark.parametrize("test_input,expected_output,expectation",
                        [("{{fa_entry_uuid}}", [('fa_entry_uuid', '')], does_not_raise()),
                        ("{{entry_uuid}}{{fa_entry_uuid}}", [('entry_uuid', ''), ('fa_entry_uuid', '')], does_not_raise()),
                        ("{{fa_entry_uuid}}:", [('fa_entry_uuid', ':')], does_not_raise()),
                        ("{{fa_entry_uuid}}::::", [('fa_entry_uuid', '::::')], does_not_raise()),
                        ("{{fa_entry_uuid}}:{{username}}", [('fa_entry_uuid', ':'), ('username', '')], does_not_raise()),
                        ("{{fa_entry_uuid}}:{{username}}+", [('fa_entry_uuid', ':'), ('username', '+')], does_not_raise()),
                        (".{{fa_entry_uuid}}", [], pytest.raises(InvalidSetting)),
                        ("{{fa_entry_uuid}}a", [], pytest.raises(InvalidSetting)),
                        ("{{username}}", [], pytest.raises(InvalidSetting)),
                        ("{{fa_entry_uuid}}{{}}", [], pytest.raises(InvalidSetting)),
                        ("{{fa_entry_uuid}}{}{{username}}", [], pytest.raises(InvalidSetting)),
                        ("{{}}", [], pytest.raises(InvalidSetting)),
                        ("fa_entry_uuid", [], pytest.raises(InvalidSetting)),
                        ])
def test_funcitonal_account_setting(test_input, expected_output, expectation):
    with expectation:
        res = configure_functional_account_login(test_input)
        assert res == expected_output
