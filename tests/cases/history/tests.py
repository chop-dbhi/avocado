from django.test import TestCase
from avocado.models import DataContext
from avocado import history
from avocado.history.models import Revision
from avocado.conf import settings


class ObjectRevisionTest(TestCase):
    def test_get_model_fields(self):
        fields = sorted(history.utils.get_model_fields(DataContext))
        self.assertEqual(fields, [
            'count',
            'default',
            'description',
            'json',
            'keywords',
            'name',
            'session',
            'session_key',
            'template',
            'tree',
        ])

    def test_get_object_data(self):
        c = DataContext()
        fields = history.utils.get_model_fields(DataContext)
        data = history.utils.get_object_data(c, fields=fields)
        self.assertEqual(data, {
            'count': None,
            'default': False,
            'description': None,
            'json': {},
            'keywords': None,
            'name': None,
            'session': False,
            'session_key': None,
            'template': False,
            'tree': None,
        })

    def test_get_for_object(self):
        c1 = DataContext()
        c1.save()
        r1 = Revision.objects.create_revision(c1, fields=['name'])

        c2 = DataContext()
        c2.save()
        Revision.objects.create_revision(c2, fields=['name'])

        # Standard, model extracted from instance
        self.assertEqual(Revision.objects.get_for_object(c1)[0], r1)

        # Explicity pass model
        self.assertEqual(
            Revision.objects.get_for_object(c1, model=DataContext)[0], r1)

        # Pass queryset containing target object
        queryset = DataContext.objects.filter(pk=c1.pk)
        self.assertEqual(
            Revision.objects.get_for_object(c1, model=queryset)[0], r1)

        # Pass queryset *not* containing target object
        queryset = DataContext.objects.filter(pk=c2.pk)
        self.assertEqual(
            list(Revision.objects.get_for_object(c1, model=queryset)), [])

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

        revision = Revision.objects.create_revision(
            c, fields=['name', 'description', 'json'])

        self.assertEqual(revision.data, {
            'name': 'Test',
            'description': None,
            'json': {}
        })

        revisions = Revision.objects.get_for_object(c)
        self.assertEqual(revisions.count(), 1)

        self.assertFalse(Revision.objects.object_has_changed(c))
        self.assertEqual(revisions[0].changes, {
            'name': {'new_value': 'Test'},
            'description': {'new_value': None},
            'json': {'new_value': {}}
        })

    def test_deleted_revision(self):
        c = DataContext(name='Test', json={})
        c.save()
        fields = ['name', 'description', 'json']

        revision = Revision.objects.create_revision(
            c, fields=fields, deleted=True)

        self.assertEqual(revision.data, None)
        self.assertEqual(revision.changes, None)

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


class ModelRevisionTestCase(TestCase):
    def setUp(self):
        c1 = DataContext({'field': 1, 'operator': 'exact', 'value': 30})
        c1.save()
        Revision.objects.create_revision(c1, fields=['json'])

        c2 = DataContext({'field': 2, 'operator': 'in', 'value': [1, 2]})
        c2.save()
        Revision.objects.create_revision(c2, fields=['json'])

        self.c1 = c1
        self.c2 = c2

    def test_get_for_model(self):
        self.assertEqual(
            Revision.objects.get_for_model(DataContext).count(), 2)

    def test_latest_for_model(self):
        self.assertEqual(
            Revision.objects.latest_for_model(DataContext).object_id,
            self.c2.pk)


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

    def test_change(self):
        c = DataContext()
        c.save()

        revisions = Revision.objects.get_for_object(c)
        self.assertEqual(revisions.count(), 1)

        latest_revision = Revision.objects.latest_for_object(c)
        self.assertFalse('old_value' in latest_revision.changes)
        self.assertEqual(latest_revision.changes, {
            'json': {'new_value': {}},
            'name': {'new_value': None},
            'description': {'new_value': None}
        })

        c.name = "New Name"
        c.save()

        revisions = Revision.objects.get_for_object(c)
        self.assertEqual(revisions.count(), 2)

        latest_revision = Revision.objects.latest_for_object(c)
        self.assertEqual(latest_revision.changes, {
            'name': {'old_value': None, 'new_value': 'New Name'}
        })
