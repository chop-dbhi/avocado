from django.test import TestCase
from avocado.models import DataContext
from avocado import history
from avocado.history import utils


class RevisionTest(TestCase):
    def test_get_model_fields(self):
        fields = sorted(utils.get_model_fields(DataContext))
        self.assertEqual(fields, [
            'archived',
            'count',
            'default',
            'description',
            'json',
            'keywords',
            'name',
            'published',
            'session',
            'session_key',
            'template',
        ])

    def test_get_object_data(self):
        c = DataContext()
        fields = utils.get_model_fields(DataContext)
        data = utils.get_object_data(c, fields=fields)
        self.assertEqual(data, {
            'archived': False,
            'count': None,
            'default': False,
            'description': None,
            'json': {},
            'keywords': None,
            'name': None,
            'published': False,
            'session': False,
            'session_key': None,
            'template': False,
        })

    def test_latest_for_object(self):
        c = DataContext()
        c.save()
        self.assertEqual(history.Revision.objects.latest_for_object(c), None)

    def test_object_has_changed(self):
        c = DataContext()
        c.save()
        # No existing revisions, so this is true
        self.assertTrue(history.Revision.objects.object_has_changed(c))

    def test_create_revision(self):
        c = DataContext(name='Test', json={})
        c.save()

        revision = history.Revision.objects.create_revision(c,
            fields=['name', 'description', 'json'])

        self.assertEqual(revision.data, {
            'name': 'Test',
            'description': None,
            'json': {}
        })

        revisions = history.Revision.objects.get_for_object(c)
        self.assertEqual(revisions.count(), 1)

        self.assertFalse(history.Revision.objects.object_has_changed(c))

    def test_register(self):
        history.register(DataContext, fields=['name', 'description', 'json'])
        self.assertTrue(DataContext in history.registry)
        self.assertEqual(history.registry[DataContext], {
            'fields': ('json', 'name', 'description'),
            'dispatch_uid': 'DataContext_revision',
        })

        history.unregister(DataContext)
        self.assertFalse(DataContext in history.registry)

    def test_apply(self):
        c = DataContext({'field': 1, 'operator': 'exact', 'value': 30})
        c.save()

        revision = history.Revision.objects.create_revision(c, fields=['json'])

        c.json['value'] = 50
        c.save()

        revision.apply(c)
        self.assertEqual(c.json['value'], 30)


class AutoRevisionTest(TestCase):
    def setUp(self):
        history.register(DataContext, fields=['name', 'description', 'json'])

    def tearDown(self):
        history.unregister(DataContext)

    def test_nochange(self):
        c = DataContext()
        c.save()

        revisions = history.Revision.objects.get_for_object(c)
        self.assertEqual(revisions.count(), 1)

        # No changes, no new revision
        c.save()
        self.assertEqual(revisions.count(), 1)
