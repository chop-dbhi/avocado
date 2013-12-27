from django.test import TestCase
from avocado.models import DataField
from ...models import Record, RecordSet


class SetsTestCase(TestCase):
    fixtures = ['sets.json']

    def test_datafield_properties(self):
        [RecordSet(name=u'Set {0}'.format(i)).save() for i in xrange(10)]
        f = DataField(app_name='tests', model_name='recordset',
                      field_name='id')
        self.assertEqual(list(f.values()), [1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
        self.assertEqual(list(f.labels()), ['Set 0', 'Set 1', 'Set 2', 'Set 3',
                                            'Set 4', 'Set 5', 'Set 6', 'Set 7',
                                            'Set 8', 'Set 9'])

    def test_translator(self):
        s = RecordSet()
        s.save()
        objs = [Record(pk=i) for i in xrange(1, 11)]
        s.bulk(objs)

        f = DataField(app_name='tests', model_name='recordset',
                      field_name='id')
        trans = f.translate(value=s.pk, tree=Record)
        self.assertEqual(unicode(trans['query_modifiers']['condition']),
                         "(AND: ('recordset__id__exact', 1))")
