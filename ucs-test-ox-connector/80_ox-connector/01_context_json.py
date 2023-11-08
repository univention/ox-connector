#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
## desc: Check context.json file
## tags: [apptest]
## roles: []
## exposure: safe
## packages:
##   - univention-ox

import json
import os

'''
Tests to check the context json file.
This test file included several tests to check the context json file.
Issue: https://git.knut.univention.de/univention/open-xchange/provisioning/-/issues/39
'''


def test_context_json_file():
    """
    Checks if contexts.json is set correctly
    """
    contexts_json_path = ('/var/lib/univention-appcenter/apps/ox-connector/data'
                          '/secrets/contexts.json')  # Path to the contexts.json file
    expected_keys = ["adminpass",
                     "adminuser"]  # Keys that should be present in each context entry

    try:
        # Read and parse the contexts.json file
        with open(contexts_json_path, 'r') as file:
            try:
                # Load the JSON data
                contexts_json = json.load(file)
                assert isinstance(contexts_json,
                                  dict), ("Invalid JSON format: contexts.json should "
                                          "be a dictionary")
            except json.JSONDecodeError:
                print("Error: Invalid JSON format in contexts.json")
                contexts_json = {}

            # Check if the master entry exists
            assert 'master' in contexts_json, "Missing 'master' entry in contexts.json"

            # Get master password from /etc/ox-secrets/master.secret file
            master_secret_path = '/etc/ox-secrets/master.secret'
            assert os.path.exists(
                master_secret_path), (f"Error: Master secret file not f"
                                      f"ound at {master_secret_path}")
            with open(master_secret_path, 'r') as master_secret_file:
                ox_master_password = master_secret_file.read().strip()

            # Compare master password with the value in the JSON for 'master' context
            if 'master' in contexts_json and 'adminpass' in contexts_json['master']:
                json_master_adminpass = contexts_json['master']['adminpass']
                assert ox_master_password == json_master_adminpass, (
                    "Master password does not match the value in contexts.json for "
                    "'master' context")

                # Iterate over all context entries and compare passwords
                for context_number, context_credentials in contexts_json.items():
                    if context_number != 'master':
                        if all(key in context_credentials for key in expected_keys):
                            context_secret_path = (f'/etc/ox-secrets/context'
                                                   f'{context_number}.secret')
                            # Only check for password match if the secret file exists
                            # (as it sometimes may not exist)
                            if os.path.exists(context_secret_path):
                                with open(context_secret_path,
                                          'r') as context_secret_file:
                                    context_password = context_secret_file.read(

                                    ).strip()
                                json_adminpass = context_credentials['adminpass']
                                assert context_password == json_adminpass, (
                                    f"Password for context {context_number} does not "
                                    f"match the value in contexts.json for context "
                                    f"{context_number}")
                            else:
                                print(
                                    f"Error: Context {context_number} secret file not"
                                    f" found at {context_secret_path}")
                        else:
                            print(
                                f"Error: Invalid structure for context "
                                f"{context_number} in contexts.json. Missing required "
                                f"keys: {', '.join(expected_keys)}")

                print(
                    "JSON validation and password checks for contexts.json passed "
                    "successfully.")

    except FileNotFoundError:
        print("Error: contexts.json file not found.")
        raise
    except AssertionError as e:
        print(f"Error: {e}")
        raise e
    except Exception as e:
        print(f"Error: An unexpected error occurred - {e}")
        raise e