# AGENTS.md — OX-Connector

Guidance for AI agents (and humans) working in this repository. It explains
**what the connector does**, **how data flows**, **where the important code
lives**, and **how to run and test it**. Read this before touching sync logic.

---

## 1. What this project is

The **OX Connector** is a **Univention (Nubus) provisioning connector**. It is a
**one-directional synchronizer**: it reads identity data from **UCS / UDM
(the LDAP directory)** and provisions it into **Open-Xchange (OX) App Suite** via
OX's **SOAP provisioning API**.

```
UCS / UDM (LDAP)  ──leading system──▶  OX App Suite (via SOAP)
```

UDM is always authoritative. The connector never writes back to LDAP (it only
keeps a small local bookkeeping database, see §6).

### Two runtimes, one shared core

The same business logic ships in two deployment flavors:

| Flavor | Entry point | Trigger source | State store |
|--------|-------------|----------------|-------------|
| **UCS App Center app** (`ox-connector`) | `app/listener_trigger` | App Center Listener + Converter → JSON files | **SQLite** (`ox-connector.db`) |
| **Standalone / Nubus for Kubernetes** | `standalone-files/consumer.py` | Nubus Provisioning API message queue | **dbm.gnu** key-value stores |

Both funnel every change into the single shared dispatcher
`univention.ox.provisioning.run()`.

### Tech stack

- **Python 3** (legacy 2.7/3.8 compatibility remnants exist; target `>=3.9`).
- Key deps: `zeep` (SOAP), `python-ldap`, `sqlalchemy` (SQLite queue),
  `tenacity` (retries), `six`. Standalone adds `pydantic-settings`,
  `nubus-provisioning-consumer`, `udm-rest-api-client`.
- Packaged as two `setuptools` sub-packages; the root `pyproject.toml` is a
  `uv` dev metapackage that wires them together for local dev/tests.

---

## 2. Repository layout

```
connector/
├── univention-ox-provisioning/     # CORE business logic (backend-agnostic)
│   └── univention/ox/provisioning/
│       ├── __init__.py               # run() dispatcher — the heart
│       ├── models.py                 # TriggerObject (the unit of work)
│       ├── db.py                     # SQLite queue: Task / Old / Dead / Relation + CLI
│       ├── helpers.py                # Skip, monkey-patch hooks, DN normalization
│       ├── key_value_store.py        # dbm.gnu store (standalone flavor)
│       ├── default_user_mapping.py   # ATTRIBUTE MAPPING (LDAP → OX)  ← metadata
│       ├── users.py                  # user create/modify/delete + mapping application
│       ├── contexts.py groups.py resources.py
│       ├── accessprofiles.py         # capability_map + writes .properties file
│       ├── functional_account.py shared_account.py deputy_permissions.py
│
├── univention-ox-soap-api/         # SOAP client library
│   └── modules/univention/ox/soap/
│       ├── backend_base.py           # abstract OxObject models + class registry
│       ├── backend.py                # SoapBackend (zeep) concrete impl
│       ├── config.py                 # ALL env-var configuration + context credentials
│       ├── services.py credentials.py types.py
│
├── standalone-files/               # Nubus/K8s entry point
│   ├── consumer.py                   # async message-queue consumer (main entry)
│   ├── config.py migrate.py
│
├── app/                            # UCS App Center app definition
│   ├── ini                           # app metadata + ListenerUDMModules list
│   ├── inst                          # join script (LDAP schema, UDM modules)
│   ├── listener_trigger              # UCS entry point (SQLite queue processor)
│   ├── settings configure env
│
├── udm/                            # UDM handlers/hooks/syntax + translations
├── ox-extension/                   # OX server-side extension
├── bin/                            # CLIs: rebuild-old.db, update/remove-ox-db-cache
├── tests/                          # pytest integration tests (live UCS or K8s)
├── unit_tests/                     # pytest unit tests
├── ucs-test-ox-connector/          # ucs-test packaged tests (.deb, Jenkins)
├── helm/ helm-unittests/           # K8s Helm charts + tests
└── docs/ox-connector-app/          # Sphinx docs (architecture.rst is authoritative)
```

---

## 3. Metadata: the attribute mapping

The connector's central "metadata" is the **LDAP → OX attribute mapping**.

- **Compile-time default:** `DEFAULT_USER_MAPPING` in
  `univention-ox-provisioning/univention/ox/provisioning/default_user_mapping.py:62`.
  Each entry maps an **OX user property** (dict key, e.g. `display_name`,
  `email1`) to an **LDAP/UDM attribute** via the `Mapping` class:

  ```python
  "email1": Mapping("mailPrimaryAddress", nillable=False),
  "aliases": Mapping("mailAlternativeAddress", multi_value=True),
  "birthday": Mapping("birthday", special_handling=SpecialHandling.DATE),
  "image1": Mapping("jpegPhoto", special_handling=SpecialHandling.IMAGE),
  ```

  `Mapping` fields:
  - `ldap_attribute` — source UDM attribute name.
  - `nillable` — if `False`, a missing value is logged as a warning.
  - `multi_value` — keep list vs. take first element.
  - `special_handling` — one of `DEFAULT / IMAGE / DATE / IMAP_URL / SMTP_URL`
    (see `SpecialHandling`, line 33). Handled in `users.py:set_ox_property()`.
  - `alternative_attributes` — fallback source attributes.
  - `position` — index into a multi-valued attribute (e.g. business phone 1 vs 2).

- **Runtime override:** if the file
  `/var/lib/univention-appcenter/apps/ox-connector/data/AttributeMapping.json`
  exists, it fully replaces the default. Loaded by
  `users.py:get_user_mapping()` (`users.py:129`).

- **Access-profile "permission metadata":** `capability_map` in
  `accessprofiles.py:91` maps UDM accessprofile booleans (e.g. `webmail`,
  `calendar`) to OX capability names (`webmail`, `calendar`, ...). Access
  profiles are **NOT sent over SOAP** — they are written to
  `data/ModuleAccessDefinitions.properties` and applied to users via
  `change_by_module_access` in `users.py:set_user_rights()`.

- **The OX object schema** (all provisionable OX properties) is declared as
  class attributes on the abstract models in `soap/backend_base.py`
  (`User` at `backend_base.py:305`, `Context`, `Group`, `Resource`,
  `SharedAccount`, `DeputyPermission`, `ModulePermission`).

---

## 4. The dispatcher and the unit of work

### `TriggerObject` — the unit of work
`models.py:5`. A wrapper around one changed UDM object. Key fields:
`entry_uuid`, `object_type` (the UDM module), `distinguished_name`,
`attributes` (new state) and `old_attributes` (previous synced state).

Operation is derived, not stored:
- `was_added()` — has new attributes, no old DN.
- `was_modified()` — has both.
- `was_deleted()` — `attributes is None` but `old_attributes` set.
- `set_attr()` / `was_enriched()` — used by handlers to write bookkeeping
  values (e.g. `oxDbId`, `oxDbUsername`, `oxDbGroupname`) back onto the object
  so they get persisted into the `Old` snapshot after success.

### `run(obj)` — the single choke point
`__init__.py:87`. Dispatches by `object_type × operation`:

| `object_type` (UDM module) | Handler module |
|----------------------------|----------------|
| `oxmail/oxcontext` | `contexts.py` |
| `oxmail/accessprofile` | `accessprofiles.py` |
| `users/user` | `users.py` |
| `oxresources/oxresources` | `resources.py` |
| `groups/group` | `groups.py` (via `get_group_objs`, split per context) |
| `oxmail/functional_account` | `functional_account.py` (via `get_account_objs`) |
| `oxmail/shared_account` | `shared_account.py` |
| `oxmail/shared_account_permission` | `shared_account.py` |

Notes:
- `Skip` (helpers.py:41) is raised to abort processing an object gracefully
  (e.g. missing `oxContext`, or the object is the context admin).
- `NoContextAdminPassword` is caught and the task is ignored (can't act without
  credentials for that context).
- Groups and functional accounts are **fanned out per OX context**
  (`get_group_objs` / `get_account_objs`), because members can live in
  different contexts and each context is provisioned separately.

### Shared-account quirks (non-obvious invariants)
- **`SharedAccount` is a deliberately minimal SOAP model.** It exposes only
  `name / display_name / primaryEmail / email1 / password`
  (`soap/backend_base.py:277`), mirrored 1:1 in `SoapSharedAccount._base2soap`
  (`backend.py`). `password` is **always hardcoded to `"dummy"`**
  (`shared_account.py:78`) — the WSDL requires the field, but shared accounts
  cannot log in and OX ignores the DB password (LDAP is authoritative). Do not
  assume other user-like attributes (language/timezone/IMAP/SMTP) exist here;
  adding them requires extending the model, `_base2soap`, and confirming the OX
  WSDL type supports them.
- **`shared_account_permission` never syncs to OX directly.**
  `modify_shared_account_permission` (`shared_account.py:335`) only re-queues the
  *related* objects it points at (via `search_src_of_relation` + the
  `update_group_queue` hook). This is why the pipeline processes
  `shared_account_permission` **before** `shared_account` — the permission change
  re-evaluates the accounts that reference it.
- **User→SharedAccount conversion is driven by the old object's type.**
  `modify_shared_account` (`shared_account.py:283`) detects that the previous
  snapshot was a `users/user` and calls OX's
  `convert_user_to_shared_account` service instead of creating fresh, reusing the
  existing `oxDbId`.

---

## 5. The processing pipeline (ordering matters)

There is **no separate pipeline framework** — the "pipeline" is the **ordered
pass over the task queue by UDM module**. Order exists because objects have
dependencies (a user needs its context; a group needs its members' OX IDs).

**UCS flavor** — `app/listener_trigger:155`:

```
1. oxmail/oxcontext                (create contexts first)
2. oxmail/accessprofile
3. users/user
4. groups/group
5. oxmail/functional_account
6. oxmail/shared_account_permission
7. oxmail/shared_account
8. oxresources/oxresources
9. oxmail/oxcontext  (again — context cleanup/deletion pass, empty attrs)
```

**Standalone flavor** — `consumer.py` processes messages as they arrive from the
queue (`OXConsumer.topics`, `consumer.py:240`); ordering/retry is handled by the
Nubus Provisioning API and message redelivery rather than a local ordered scan.

---

## 6. Data flow end-to-end

```
        LDAP change (UDM)
              │
   ┌──────────┴───────────────────────────┐
   │ UCS App Center                        │ Nubus / K8s
   ▼                                       ▼
Listener writes {ts}.json           Provisioning API queue
 (UniventionObjectIdentifier)              │
   │                                       │
Listener Converter resolves UDM      consumer.handle_message()
 attrs → data/listener/{ts}.json       (config.py:body.old / body.new)
   │  triggers container script            │
   ▼                                       ▼
listener_trigger.main()             OXConsumer.create/modify/remove()
   │  add_task() → SQLite `tasks`          │  builds TriggerObject
   │  ordered scan → build TriggerObject   │  state in dbm.gnu KeyValueStores
   └────────────────┬──────────────────────┘
                    ▼
     univention.ox.provisioning.run(obj)      # __init__.py:87 — SHARED CORE
                    │  dispatch by object_type × operation
                    ▼
     users.py / contexts.py / groups.py / ...
                    │  apply DEFAULT_USER_MAPPING → build OxObject
                    ▼
     get_ox_integration_class("SOAP", "User")   # backend_base registry
                    ▼
     SoapBackend (zeep)  ──▶  OX App Suite SOAP API   # backend.py + services.py
```

### Result handling (UCS flavor), `listener_trigger.py:166`
- **Success + deletion** → remove `Old` row + remove task.
- **Success otherwise** → `move_task_to_old(task, obj.attributes)` (this
  becomes the new snapshot, including enriched bookkeeping attrs).
- **HTTP/Connection/Timeout error** → increment error count, **stop the whole
  run**, write `restart.json`, sleep with backoff, retry later. Contexts are so
  critical that any context error also stops the run.
- **Other error** → `move_task_to_morgue(task, traceback)` (unless
  `OX_CONNECTOR_STOP_ON_ERROR` or it's a context task).

### Result handling (standalone flavor), `consumer.py:263`
An unhandled exception is **re-raised** so the message is *not* acknowledged and
gets redelivered; the process restarts with clean state (K8s/Docker restarts
it). Special case: when `isOxUser`/`isOxGroup` toggles on a modify, it is turned
into a create or delete instead (`consumer.py:301`).

---

## 7. Local bookkeeping database (the `old` state)

The connector must know the **OX-internal object ID** (`oxDbId`) it created,
because OX group membership and updates reference OX IDs, not LDAP names.
It keeps a **last-successfully-synced snapshot** locally.

### UCS flavor — SQLite (`db.py`)
File: `/var/lib/univention-appcenter/apps/ox-connector/data/listener/ox-connector.db`

Tables (SQLAlchemy models in `db.py`):
- **`tasks`** (`Task`, `db.py:143`) — the pending work queue, ordered by
  `created_at`. Has `status` and `num_errors`.
- **`old`** (`Old`, `db.py:116`) — last successful snapshot per object
  (`obj_id = univentionObjectIdentifier`); holds enriched attrs like `oxDbId`.
  This is what `helpers.get_old_obj` reads.
- **`morgue`** (`Dead`, `db.py:100`) — failed tasks parked for manual review,
  with the error message.
- **`relations`** (`Relation`, `db.py:74`) — cross-object references (e.g.
  which shared-account permissions point at a user), used to re-queue dependent
  objects when their target changes.

### Standalone flavor — dbm.gnu (`key_value_store.py`)
`consumer.py:50` maintains several `KeyValueStore` files (`contexts.db`,
`ox_db_id.db`, `usernames.db`, `non_ox_objs.db`, `shared_permissions.db`,
`univention_object_identifier.db`) keyed by normalized DN. Missing entries fall
back to a **live OX SOAP lookup** (`_search_ox_context_for_user`,
`consumer.py:90`).

---

## 8. The "glue": monkey-patched hooks

The core (`univention-ox-provisioning`) is **backend-agnostic**. It declares
`NotImplementedError` stubs in `helpers.py` that each entry point overwrites at
import time. **This is the crucial decoupling mechanism** — trace these when
debugging "where does old state come from?":

| Hook (`helpers.py`) | UCS patch (`listener_trigger`) | Standalone patch (`consumer.py`) |
|---------------------|--------------------------------|----------------------------------|
| `get_old_obj` (`:82`) | `_get_old_object` → SQLite `Old` | `_get_existing_object_ox_id` → dbm + live OX lookup |
| `update_group_queue` (`:92`) | `_update_group_queue` → new SQLite task | (queue-driven) |
| `add_relation` / `remove_complete_relation` / `search_src_of_relation` | SQLite `Relation` funcs | — |

`get_db_id(dn)` (`helpers.py:86`) resolves an OX ID for a member by calling
`get_old_obj` — this is how groups (`groups.py:update_group`) resolve member IDs
without hitting OX.

---

## 9. SOAP layer

- **Registry / factory:** `get_ox_integration_class("SOAP", "User")`
  (`backend_base.py:59`). Concrete classes self-register via `BackendMetaClass`
  when `univention.ox.soap.backend` is imported.
- **Abstract models:** `backend_base.py` — `OxObject` base + `Context`, `Group`,
  `Resource`, `User`, `SharedAccount`, `SecondaryAccount`, `UserCopy`,
  `DeputyPermission`, `ActiveDeputyPermission`, `ModulePermission`. Each exposes
  `create() / modify() / remove() / from_ox() / list()`.
- **Concrete impl:** `SoapBackend` in `backend.py` (zeep client). `_base2soap`
  maps python attributes → SOAP fields.
- **Config & credentials:** `soap/config.py`. All behavior is env-driven:
  - `OX_SOAP_SERVER`, `DEFAULT_CONTEXT`, `OX_LANGUAGE`, `LOCAL_TIMEZONE`,
    `OX_IMAP_SERVER`, `OX_SMTP_SERVER`, `OX_IMAP_LOGIN`.
  - `OX_USER_IDENTIFIER` / `OX_GROUP_IDENTIFIER` — which LDAP attr is the OX
    "name" (default `username` / `name`; can be `entryUUID`).
  - `OX_ENABLE_DEPUTY_PERMISSIONS`, `OX_ENABLE_SHARED_ACCOUNT`.
  - Per-context admin credentials read from
    `OX_CREDENTIALS_FILE` (default `/etc/ox-secrets/ox-contexts.json`);
    missing entry → `NoContextAdminPassword`.

---

## 10. Handler conventions (important invariants)

All object handlers follow the same defensive pattern — preserve it when
editing:

- **create → modify fallback:** `create_user`/`create_group` check if the object
  already exists in OX and call `modify_*` instead (`users.py:340`,
  `groups.py:115`).
- **modify → create fallback:** if the object isn't found, modify creates it.
- **`is_ox_user` / `is_ox_group` gate:** if the object is not flagged as an OX
  object, the handler **deletes** it from OX instead of creating/modifying
  (`users.py:336`, `groups.py:112`). The `isOxUser`/`isOxGroup` UDM flags are
  the on/off switch for OX provisioning.
- **Empty groups are deleted:** a group with no members is removed rather than
  created (`groups.py:124`). Deleting a user prunes now-empty groups
  (`users.py:572`).
- **Context moves** use OX `UserCopy` then delete the source
  (`users.py:createuser(..., user_copy_service=...)`, `users.py:474`).
- **After success**, handlers call `obj.set_attr("oxDbId", ...)` /
  `"oxDbUsername"` / `"oxDbGroupname"` so the ID is stored in the `Old` snapshot.
- **Context admin is never touched** (`get_user_id` raises `SkipContextAdmin`,
  `users.py:315`).

---

## 11. Tests

| Location | Framework | Scope |
|----------|-----------|-------|
| `tests/` | **pytest** | Integration tests against a **live UCS or K8s** deployment. `conftest.py` holds fixtures; `--k8s` switches to `k8s_support.py`. Creates objects via UDM REST (`udm_rest.py`) and asserts via SOAP. |
| `unit_tests/` | pytest | Pure unit tests, e.g. `test_provisioning_init.py` (tests `run()` dispatch). No live services. |
| `univention-ox-soap-api/tests/` | pytest | `test_config.py` — SOAP config logic. |
| `ucs-test-ox-connector/` | ucs-test (.deb) | Runs on real UCS via Jenkins (`80_ox-connector/*.py`). |
| `helm-unittests/` | helm unittest | K8s chart tests. |

Integration test files: `test_user.py`, `test_group.py`, `test_context.py`,
`test_resource.py`, `test_accessprofile.py`, `test_deputy_permission.py`,
`test_shared_account.py`, `test_function_account.py`,
`test_functional_account_setting.py`, `test_user_attribute_mapping.py`,
`test_cache.py`.

### Running tests

- Unit tests (no infra), from repo root:
  ```bash
  uv run pytest unit_tests -v
  ```
  Root `pyproject.toml` sets `pythonpath = ["standalone-files"]` and defines the
  `k8s_skip` marker.

- Integration tests need a live deployment and typically run **inside the app
  container / consumer container** (they share OX credentials state). The
  standalone dev harness (`README.dev.md`) drives this:
  ```bash
  docker compose run --remove-orphans dev ssh <ucs-ip> test -s -v
  docker compose run --remove-orphans dev kubernetes <ns> test -s -v
  ```
  Inside the UCS app container the docs use:
  ```bash
  python3 -m pytest -l -v tests
  ```

> Integration tests create and delete real objects in UDM and OX. Never point
> them at production. Use the dev harness `udm` subcommand to clean up leftovers
> after a crash (see `README.dev.md`).

---

## 12. Admin / debugging CLI

The SQLite queue has a full CLI (`db.py:1000`, run inside the app container):

```bash
python -m univention.ox.provisioning.db <action> [--options]
```

Useful actions:
- `show-item --obj-id <uuid>` — where an object is across old/tasks/morgue.
- `search-tasks` / `summarize-tasks` — inspect the pending queue.
- `search-morgue` / `summarize-morgue` — inspect failures.
- `resync-item --obj-id <uuid>` — re-provision using latest UDM data.
- `retry-from-morgue --obj-id <uuid>` — retry with the exact failed data.
- `remove-from-morgue --obj-id <uuid>` — drop a failed task.
- `rewrite-ox-db-id` — re-fetch OX internal IDs live and fix the `old` table.

Additional CLIs live in `bin/` (`rebuild-old.db`, `update-ox-db-cache`,
`remove-ox-db-cache`).

---

## 13. Working-in-this-repo checklist for agents

1. **Change sync behavior?** Edit the handler in
   `univention-ox-provisioning/univention/ox/provisioning/<type>.py`, then make
   sure both entry points still work — they share `run()` but persist state
   differently (SQLite vs dbm). Check the monkey-patched hooks in §8.
2. **Change/extend attributes?** Edit `default_user_mapping.py` (and remember
   `AttributeMapping.json` can override at runtime). If a new OX property is
   needed, also add it to the model in `soap/backend_base.py` and the mapping in
   `soap/backend.py`.
3. **Change ordering/dependencies?** The `listener_trigger.py:155` list is
   load-bearing; contexts must come first and be revisited last.
4. **Never write to LDAP** — the connector is one-directional; only the local
   bookkeeping DB is writable.
5. **Preserve the create↔modify fallbacks and the `is_ox_*` delete-gate** (§10);
   they are relied upon for idempotency and for turning objects off.
6. **Verify** with `uv run pytest unit_tests` for logic changes; use the dev
   harness for integration behavior.
7. **Authoritative prose docs:** `docs/ox-connector-app/architecture.rst`.

---

## 14. Glossary

- **UDM** — Univention Directory Manager, the object layer over UCS LDAP.
- **UDM module** — object class, e.g. `users/user`, `groups/group`,
  `oxmail/oxcontext`.
- **Context** — an OX tenant/partition; users/groups live inside one context.
- **`oxDbId`** — OX-internal object ID, cached locally after a successful sync.
- **`isOxUser` / `isOxGroup`** — UDM flags that enable OX provisioning for an
  object; unset means "delete from OX".
- **Old / morgue / tasks** — the three SQLite tables: last good snapshot /
  failed / pending.
- **Access profile** — a named set of OX capabilities (roles), stored in a
  `.properties` file, applied to users via SOAP `change_by_module_access`.
