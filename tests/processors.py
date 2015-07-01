from avocado.models import DataContext
from avocado.query.pipeline import QueryProcessor


class ManagerQueryProcessor(QueryProcessor):
    def __init__(self, *args, **kwargs):
        kwargs['context'] = DataContext(json={
            'field': 'tests.employee.is_manager',
            'operator': 'exact',
            'value': True,
        })

        super(ManagerQueryProcessor, self).__init__(*args, **kwargs)
