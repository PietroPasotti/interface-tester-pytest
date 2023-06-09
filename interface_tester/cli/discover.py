from pathlib import Path

import typer

from interface_tester.collector import _CharmTestConfig, collect_tests
from interface_tester.interface_test import SchemaConfig, _InterfaceTestCase


def pprint_tests(
    path: Path = typer.Argument(
        Path(), help="Path to the root of a charm-relation-interfaces-compliant repository root."
    ),
    include: str = typer.Option("*", help="String for globbing interface names."),
):
    """Pretty-print a listing of the interface tests specified in a charm-relation-interfaces repository."""
    return _pprint_tests(path, include)


def _pprint_tests(path: Path = Path(), include="*"):
    """Pretty-print a listing of the interface tests specified in this repository."""
    print(f"collecting tests from root = {path.absolute()}...")
    tests = collect_tests(path=path, include=include)
    print("Discovered:")

    def pprint_case(case: "_InterfaceTestCase"):
        state = "yes" if case.input_state else "no"
        schema_config = case.schema if isinstance(case.schema, SchemaConfig) else "custom"
        print(f"      - {case.name}:: {case.event} (state={state}, schema={schema_config})")

    for interface, versions in tests.items():
        if not versions:
            print(f"{interface}: <no tests>")
            print()
            continue

        print(f"{interface}:")

        for version, roles in versions.items():
            print(f"  - {version}:")

            by_role = {role: roles[role] for role in {"requirer", "provider"}}

            for role, test_spec in by_role.items():
                print(f"   - {role}:")

                tests = test_spec["tests"]
                schema = test_spec["schema"]

                for test_cls in tests:
                    pprint_case(test_cls)
                if not tests:
                    print(f"     - <no tests>")

                if schema:
                    # todo: check if unit/app are given.
                    print(f"     - schema OK")
                else:
                    print(f"     - schema NOT OK")

                charms = test_spec["charms"]
                if charms:
                    print("     - charms:")
                    charm: _CharmTestConfig
                    for charm in charms:
                        if isinstance(charm, str):
                            print(f"       - <BADLY FORMATTED>")
                            continue

                        custom_test_setup = "yes" if charm.test_setup else "no"
                        print(
                            f'       - {charm.name} ({charm.url or "NO URL"}) '
                            f"custom_test_setup={custom_test_setup}"
                        )

                else:
                    print("     - <no charms>")

        print()


if __name__ == "__main__":
    _pprint_tests(Path())
