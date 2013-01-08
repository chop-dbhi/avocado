import time
from django.test import TestCase
from django.db import IntegrityError
from avocado.models import DataField
from avocado.sets.models import ObjectSetError
from .models import Record, RecordSet, RecordSetObject


class SetsTestCase(TestCase):
    fixtures = ['sets.json']

    def test_empty_set(self):
        s = RecordSet()
        s.save()
        self.assertEqual(s.count, 0)

    def test_methods_require_pk(self):
        s = RecordSet()
        r1 = Record(pk=1)

        self.assertRaises(ObjectSetError, s.add, r1)
        self.assertRaises(ObjectSetError, s.remove, r1)
        self.assertRaises(ObjectSetError, s.replace, r1)
        self.assertRaises(ObjectSetError, s.clear)
        self.assertRaises(ObjectSetError, s.flush)

    def test_invalid_type(self):
        s = RecordSet()
        s.save()

        self.assertRaises(TypeError, s.add, 1)

    def test_add(self):
        s = RecordSet()
        s.save()

        r1 = Record(pk=1)
        self.assertTrue(s.add(r1))
        self.assertEqual(s.count, 1)
        self.assertFalse(s.add(r1))
        self.assertEqual(s.count, 1)

        self.assertTrue(s.remove(r1))
        self.assertEqual(s.count, 0)
        self.assertTrue(s.add(r1))
        self.assertEqual(s.count, 1)

        self.assertEqual(s._all_set_objects.count(), 1)

    def test_bulk(self):
        s = RecordSet()
        s.save()

        objs = [Record(pk=i) for i in xrange(5)]
        objs2 = [Record(pk=i) for i in xrange(5, 10)]

        # Load 5
        self.assertEqual(s.bulk(objs), 5)
        self.assertEqual(s.count, 5)

        # Another 5
        self.assertEqual(s.bulk(objs2), 5)
        self.assertEqual(s.count, 10)

        # But not again..
        self.assertRaises(IntegrityError, s.bulk, [objs[3]])

    def test_remove(self):
        s = RecordSet()
        s.save()

        r1 = Record(pk=1)
        self.assertTrue(s.add(r1))
        self.assertTrue(s.remove(r1))
        self.assertEqual(s.count, 0)
        self.assertFalse(s.remove(r1))

        # The `removed` record still exists
        self.assertEqual(s._all_set_objects.count(), 1)

    def test_remove_delete(self):
        s = RecordSet()
        s.save()

        r1 = Record(pk=1)
        self.assertTrue(s.add(r1))
        self.assertEqual(s.count, 1)
        s.remove(r1, delete=True)
        self.assertEqual(s.count, 0)

        # Real delete
        self.assertEqual(s._all_set_objects.count(), 0)

    def test_update(self):
        s = RecordSet()
        s.save()

        # Initial 5
        self.assertEqual(s.update([Record(pk=i) for i in xrange(0, 10, 2)]), 5)
        self.assertEqual(s.count, 5)

        # Adding the same doesn't do anything
        self.assertEqual(s.update([Record(pk=i) for i in xrange(0, 10, 2)]), 0)
        self.assertEqual(s.count, 5)

        # Add everything, only 5 get added
        self.assertEqual(s.update([Record(pk=i) for i in xrange(10)]), 5)
        self.assertEqual(s.count, 10)

        # The `removed` records still exist
        self.assertEqual(s._all_set_objects.count(), 10)

    def test_replace(self):
        s = RecordSet()
        s.save()

        s.update([Record(pk=i) for i in xrange(3)])
        self.assertEqual(s.replace([Record(pk=i) for i in xrange(2, 6)]), 4)

        # The `removed` records still exist
        self.assertEqual(s._all_set_objects.count(), 6)

    def test_replace_delete(self):
        s = RecordSet()
        s.save()

        s.bulk([Record(pk=i) for i in xrange(3)])
        self.assertEqual(s.count, 3)
        self.assertEqual(s.replace([Record(pk=i) for i in xrange(2, 6)], delete=True), 4)
        self.assertEqual(s.count, 4)

        # Original ones removed
        self.assertEqual(s._all_set_objects.count(), 4)

    def test_clear(self):
        s = RecordSet()
        s.save()

        s.update([Record(pk=i) for i in xrange(10)])
        self.assertEqual(s.clear(), 10)
        self.assertEqual(s.count, 0)

        # The `removed` records still exist
        self.assertEqual(s._all_set_objects.count(), 10)

    def test_clear_delete(self):
        s = RecordSet()
        s.save()

        s.bulk([Record(pk=i) for i in xrange(10)])
        self.assertEqual(s.clear(delete=True), 10)

        # The `removed` records still exist
        self.assertEqual(s._all_set_objects.count(), 0)

    def test_flush(self):
        s = RecordSet()
        s.save()

        s.update([Record(pk=i) for i in xrange(3)])
        s.replace([Record(pk=i) for i in xrange(2, 6)])

        # The `removed` records still exist
        self.assertEqual(s._all_set_objects.count(), 6)

        s.flush()
        # The `removed` records have been deleted
        self.assertEqual(s._all_set_objects.count(), 4)

    def test_perf(self):
        "Compares performance of bulk load vs. an update"
        s = RecordSet()
        s.save()

        Record.objects.all().delete()

        # Only test 100. SQLite limitation..
        objs = [Record(pk=i) for i in xrange(100)]
        Record.objects.bulk_create(objs)

        t0 = time.time()
        s.update(objs)
        t1 = time.time() - t0

        RecordSetObject.objects.all().delete()

        t0 = time.time()
        s.bulk(objs)
        t2 = time.time() - t0

        # 10-fold difference
        self.assertTrue(t2 * 10 < t1)

    def test_iter(self):
        s = RecordSet()
        s.save()
        objs = [Record(pk=i) for i in xrange(1, 11)]
        s.bulk(objs)
        self.assertEqual(list(s), objs)

    def test_contains(self):
        s = RecordSet()
        s.save()
        objs = [Record(pk=i) for i in xrange(1, 11)]
        s.bulk(objs)
        self.assertTrue(objs[0] in s)
        self.assertTrue(objs[7] in s)
        self.assertFalse(Record(pk=12) in s)

    # Avocado integration
    def test_datafield_properties(self):
        [RecordSet(name='Set {0}'.format(i)).save() for i in xrange(10)]
        f = DataField(app_name='sets', model_name='recordset', field_name='id')
        self.assertEqual(f.values, (1, 2, 3, 4, 5, 6, 7, 8, 9, 10))
        self.assertEqual(f.labels, ('Set 0', 'Set 1', 'Set 2', 'Set 3',
            'Set 4', 'Set 5', 'Set 6', 'Set 7', 'Set 8', 'Set 9'))

    def test_translator(self):
        s = RecordSet()
        s.save()
        objs = [Record(pk=i) for i in xrange(1, 11)]
        s.bulk(objs)

        f = DataField(app_name='sets', model_name='recordset', field_name='id')
        trans = f.translate(value=s.pk, tree=Record)
        self.assertEqual(str(trans['query_modifiers']['condition']),
            "(AND: ('recordset__id__exact', 1))")
