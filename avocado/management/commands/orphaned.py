from django.core.management.base import NoArgsCommand

from avocado.models import Field

class Command(NoArgsCommand):
    help = "Determines outdated or orphaned Field definitions."

    def handle_noargs(self, **options):
        fields = Field.objects.all()

        unknown_model = []
        unknown_field = []

        for f in fields:
            if f.model is None:
                unknown_model.append(f)
            elif f.field is None:
                unknown_field.append(f)

        if unknown_model:
            print
            print 'The following Fields have an unknown model:\n'
            for f in unknown_model:
                print '\t',
                if f.is_public:
                    print '[A]',
                else:
                    print '   ',
                print f
        if unknown_field:
            print
            print 'The following Fields have an unknown field:\n'
            for f in unknown_field:
                print '\t',
                if f.is_public:
                    print '[A]',
                else:
                    print '   ',
                print f
            print
