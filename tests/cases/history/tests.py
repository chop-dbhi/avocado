from django.test import TestCase
from avocado.models import DataContext
from avocado import history
from avocado.history.models import Revision
from avocado.conf import settings


class RevisionTest(TestCase):
    def test_get_model_fields(self):
        fields = sorted(history.utils.get_model_fields(DataContext))
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
        fields = history.utils.get_model_fields(DataContext)
        data = history.utils.get_object_data(c, fields=fields)
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
        self.assertEqual(Revision.objects.latest_for_object(c), None)

    def test_object_has_changed(self):
        c = DataContext()
        c.save()
        # No existing revisions, so this is true
        self.assertTrue(Revision.objects.object_has_changed(c))

    def test_create_revision(self):
        c = DataContext(name='Test', json={})
        c.save()

        revision = Revision.objects.create_revision(c,
            fields=['name', 'description', 'json'])

        self.assertEqual(revision.data, {
            'name': 'Test',
            'description': None,
            'json': {}
        })

        revisions = Revision.objects.get_for_object(c)
        self.assertEqual(revisions.count(), 1)

        self.assertFalse(Revision.objects.object_has_changed(c))

    def test_cull_for_object(self):
        c = DataContext(name='Test')
        c.save()

        Revision.objects.create_revision(c, fields=['name'])

        for i in xrange(1, 100):
            c.name = 'Test{0}'.format(i)
            c.save()
            Revision.objects.create_revision(c, fields=['name'])

        self.assertEqual(Revision.objects.get_for_object(c).count(), 100)

        # Cull down to the maximum size defined in the settings
        Revision.objects.cull_for_object(c)
        self.assertEqual(Revision.objects.get_for_object(c).count(),
            settings.HISTORY_MAX_SIZE)

        # Cull down to an arbitrary size
        Revision.objects.cull_for_object(c, max_size=20)
        self.assertEqual(Revision.objects.get_for_object(c).count(), 20)


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

        revision = Revision.objects.create_revision(c, fields=['json'])

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

        revisions = Revision.objects.get_for_object(c)
        self.assertEqual(revisions.count(), 1)

        # No changes, no new revision
        c.save()
        self.assertEqual(revisions.count(), 1)
