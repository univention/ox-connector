# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

from univention.ox.provisioning.db import Relation


def test_relation_foreign_key_and_deletion_cascade(db_session):
    """
    DB may not validate full integrity via Foeign Key Constraints
    as relations may be added before the corresponding objects
    have been synced. They have to be deleted though if the
    corresponding object exists and is being deleted.
    """
    src_obj_id = "oxtest-xxxx-yyyy-zzzz-123456789012"
    src_obj_dn = "cn=test"

    db_session.add_relation(
        src_obj_id,
        "groups/group",
        "oxuser-xxxx-yyyy-zzzz-123456789012",
        "users/user",
        "member",
    )
    db_session.commit()
    obj_in_db = (
        db_session.query(Relation).filter_by(src_obj_id=src_obj_id).first()
    )
    assert obj_in_db is not None
    db_session.store_old(src_obj_id, "groups/group", src_obj_dn, {})
    db_session.commit()
    db_session.remove_old(src_obj_dn)
    db_session.commit()
    obj_in_db = (
        db_session.query(Relation).filter_by(src_obj_id=src_obj_id).first()
    )
    assert obj_in_db is None
