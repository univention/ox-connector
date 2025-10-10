# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH


class TriggerObject(object):
    """
    A thin wrapper over a JSON file. Holds all the information from that
    file. May also hold information of this object from a previous run
    (needs a second, backup file for that)
    """

    def __init__(
        self,
        entry_uuid,
        object_type,
        distinguished_name,
        attributes,
        options,
        path=None,
    ):
        self.entry_uuid = entry_uuid
        self.object_type = object_type
        self.distinguished_name = distinguished_name
        self.attributes = attributes
        self.options = options
        self.old_distinguished_name = None
        self.old_attributes = None
        self.old_options = None
        self.path = path  # file where it originates from
        self._old_loaded = False
        self._enriched = {}

    def load_old(self, *args, **kwargs):
        """
        Load old state.

        Subclasses must implement this if they want to support loading of old
        state. There is no common interface defined for this method.
        """
        raise NotImplementedError(
            "This implementation does not support loading old state.",
        )

    def was_added(self):
        """
        Whether this object is new. Needs the have read an old file
        for this to give a meaningful response
        """
        if self.attributes is None:
            return False
        if not self._old_loaded:
            return None
        return self.old_distinguished_name is None

    def was_modified(self):
        """
        Whether this object was modified. Needs the have read an old
        file for this to give a meaningful response
        """
        if self.attributes is None:
            return False
        if self._old_loaded is False:
            return None
        return not self.was_added() and not self.was_deleted()

    def was_deleted(self):
        """Whether this object was deleted."""
        return self.attributes is None and self.old_attributes is not None

    def was_enriched(self):
        """Whether the obj was modified via set_attr during processing."""
        return bool(self._enriched)

    def set_attr(self, attr, value):
        """Enrich an object's attributes. Will be preserved should the
        old object be kept (i.e. files are moved at the end)"""
        if self.attributes.get(attr) != value:
            self.attributes[attr] = value
            self._enriched[attr] = value

    def __repr__(self):
        return f"Object({self.object_type!r}, {self.distinguished_name!r})"
