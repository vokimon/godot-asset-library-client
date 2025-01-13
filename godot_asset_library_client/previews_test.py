import unittest
from .previews import preview_action, to_remove_previews
from yamlns import ns

class Previews_Test(unittest.TestCase):
    from yamlns.testutils import assertNsEqual

    def test__preview_action__with_implicit_op(self):
        result = preview_action(
            preview = ns(
                link='A',
                operation='insert',
            ),
            old_previews=[],
        )
        self.assertNsEqual(result, """
            #enabled: true # what about that?
            link: A
            operation: insert
        """)

    def test__preview_action__new_link__insert(self):
        result = preview_action(
            preview = ns(
                link='A',
            ),
            old_previews=[],
        )
        self.assertNsEqual(result, """
            enabled: true
            link: A
            operation: insert
        """)

    def test__preview_action__existing_link__update(self):
        result = preview_action(
            preview = ns(
                link='A',
                extra_attribute='A-thumb',
            ),
            old_previews=[
                ns(
                    preview_id=666,
                    link='A',
                ),
            ],
        )
        self.assertNsEqual(result, """
            enabled: true
            operation: update
            edit_preview_id: 666 # this change name
            link: A
            extra_attribute: A-thumb
        """)


    def test__preview_action__missmatch_link__insert(self):
        result = preview_action(
            preview = ns(
                link='A',
            ),
            old_previews=[
                ns(
                    preview_id=666,
                    link='B',
                ),
            ],
        )
        self.assertNsEqual(result, """
            enabled: true
            link: A
            operation: insert
        """)

    def test__to_remove_previews(self):
        result = to_remove_previews([
            ns(link="A"),
            ns(link="B"),
        ], [
            ns(link="A", preview_id=666),
            ns(link="C", preview_id=777),
        ])
        self.assertNsEqual(ns(result=result), """
            result:
            - edit_preview_id: 777
              enabled: true
              operation: delete
        """)

