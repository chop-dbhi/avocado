from django.db import models
from django import forms

from avocado.concepts.models import ConceptAbstract
from avocado.concepts.managers import ConceptManager

__all__ = ('FieldConcept',)

class FieldConcept(ConceptAbstract):
    """The `FieldConcept' class stores off meta data about a "field of
    interest" located on another model. This, in a sense, provides a way to
    specify the fields that can be utilized by the query engine.

    There three cases in which a "field of interest" should be stored:

        defintion/vocabulary - at the very least, storing off a field provides
        the ability specify a `description' and `keywords' (or aliases) associated
        with the field.

        search criteria - the field can be associated with one or more
        `CriterionConcepts'. at minimum, this provides the ability to query by
        this field. in a more complex scenario, the field can act as a dependent
        or dependency on other fields.

        reporting - the field can be associated with one or more `ColumnConcepts'
        which allows for generating reports (results) in-browser or exporting to
        another format.
    """
    model_label = models.CharField(max_length=100, editable=False)
    field_name = models.CharField(max_length=100, editable=False)
    formfield_class = models.CharField(max_length=100, editable=False)

    objects = ConceptManager()

    class Meta(ConceptAbstract.Meta):
        verbose_name = 'field concept'
        verbose_name_plural = 'field concepts'

    def __unicode__(self):
        return u'%s' % self.name or '.'.join([self.model_label, self.field_name])

    def _get_model(self):
        if not hasattr(self, '_model'):
            app_label, model_label = self.model_label.split('.')
            self._model = models.get_model(app_label, model_label)
        return self._model
    model = property(_get_model)

    def _get_field(self):
        if not hasattr(self, '_field'):
            self._field = self.model._meta.get_field_by_name(self.field_name)[0]
        return self._field
    field = property(_get_field)

    def formfield(self, **kwargs):
        return self.field.formfield(**kwargs)

    def value_is_valid(self, value, formfield=None, **kwargs):
        if formfield is None:
            formfield = self.field.formfield(**kwargs)
        
        print formfield.__class__
        try:
            cleaned_value = formfield.clean(value)
        except forms.ValidationError, e:
            return (False, None, e.messages)
        return (True, cleaned_value, ())
# import psycopg2
# import datetime
#
# from django.conf import settings
# from django.db.models import Q
# from django.utils import simplejson
# from django.template import Context
# from django.db import models
# from django.template.loader import get_template
# from django.db.models.query import QuerySet, ValuesListQuerySet
# from ..exceptions import ConfigurationError
# from ..criteria import datatypes
# from .managers import FieldManager
#
# __all__ = ('FieldIcon', 'FieldCategory', 'Field')
#
# _models = __import__(settings.FIELD_MODELS_MODULE, fromlist='models')
#
#
# ICON_UPLOAD_PATH = 'icons'
#
# if hasattr(settings, 'ICON_UPLOAD_PATH'):
#     ICON_UPLOAD_PATH = settings.ICON_UPLOAD_PATH
#
#
# RAW_DB_CONNECTION_SETTINGS = {
#     'database': settings.DATABASE_NAME,
#     'user': settings.DATABASE_USER,
#     'password': settings.DATABASE_PASSWORD,
#     'host': settings.DATABASE_HOST,
#     'port': settings.DATABASE_PORT,
# }
#
#
# class FieldIcon(models.Model):
#     """Stores off icons that can be reused for fields. Prevents duplicates
#     and is a better interface than managing via a file-based interface.
#     """
#     name = models.CharField(max_length=30)
#     icon = models.FileField(upload_to=ICON_UPLOAD_PATH)
#
#     class Meta:
#         app_label = 'avocado'
#         ordering = ('name',)
#         verbose_name = 'field icon'
#         verbose_name_plural = 'field icons'
#
#     def __unicode__(self):
#         return u'%s' % self.name
#
#
# class FieldCategory(models.Model):
#     "Categorizes fields for display."
#     name = models.CharField(max_length=100)
#     icon = models.ForeignKey(FieldIcon, null=True, blank=True)
#     is_public = models.BooleanField('make category public?', default=True)
#     modified = models.DateTimeField(editable=False)
#
#     class Meta:
#         app_label = 'avocado'
#         ordering = ('display_name',)
#         verbose_name = 'category'
#         verbose_name_plural = 'categories'
#
#     def __unicode__(self):
#         return u'%s' % self.display_name or self.name
#
#     def save(self):
#         self.modified = datetime.datetime.now()
#         super(FieldCategory, self).save()
#
#
# class Field(models.Model):
#     """This stores meta data about a particular field which will be used for
#     display, generation of flat files for UI use, and querying.
#
#     Models defined will be assumed to be consistent between staging and
#     production implementations.
#     """
#
#     allowed_values_help_text = """
#     The `allowed_values` field can contain one of five options:
#         1. `None`
#         2. a constant bound to a model, i.e. `BAZ_CHOICES`. the loader
#             mechanism looks for model.BAZ_CHOICES
#         3. a constant bound to the model's module, i.e.
#             `module1.module2.BAZ_CHOICES`. the loader
#             will try to dynamically load the constant on that path
#         4. a callable which returns a valid sequence of pts at runtime.
#         5. a queryset object, which utilizes the `id` and `__unicode__` value
#             for the CV
#
#     The controlled vocabulary (CV) format must be as follows:
#
#         SAMPLE = (
#             (<value_used_during_query>, <display_name>),
#             ...
#         )
#
#     In the case of the queryset, this format will be constructed on-the-fly
#     using the `obj.id` and `obj.__unicode__` values.
#     """
#     DATATYPE_CHOICES = tuple([(x.name, x.name.title()) for x in datatypes.datatypes])
#
#     model = models.CharField(max_length=200, help_text='e.g. Patient')
#     field_name = models.CharField(max_length=50)
#     db_field_name = models.CharField(max_length=50)
#     description = models.TextField(blank=True)
#     datatype = models.CharField(max_length=20, choices=DATATYPE_CHOICES)
#     display_name = models.CharField(max_length=50, blank=True)
#     keywords = models.CharField(max_length=200, blank=True)
#     category = models.ForeignKey(FieldCategory, null=True, blank=True)
#     icon = models.ForeignKey(FieldIcon, null=True, blank=True)
#
#     allowed_values_callback = models.TextField(blank=True,
#         help_text=allowed_values_help_text)
#     # TODO populate this fulltext on save which runs the allowed_values_callback
#     allowed_values_fulltext = models.TextField(blank=True)
#
#     # graphic representation info
#     graphic_title = models.CharField('title', max_length=100, blank=True)
#     graphic_xaxis = models.CharField('x-axis label', max_length=100, blank=True)
#     graphic_yaxis = models.CharField('y-axis label', max_length=100, blank=True)
#     graphic_query = models.TextField('SQL query', blank=True,
#         help_text='must generate a two column table')
#
#     is_public = models.BooleanField('make this a public field?', default=False)
#     is_default = models.BooleanField('make this a default field?', default=False)
#
#     modified = models.DateTimeField(editable=False)
#
#     objects = FieldManager() # overrode the default manager
#
#     _allowed_values = None
#     _json_cache = None
#     _form_class = None
#     _model_cls = None
#
#     class Meta:
#         app_label = 'avocado'
#         ordering = ('display_name',)
#
#     def __unicode__(self):
#         return u'%s' % self.display_name or self.field_name
#
#     @property
#     def datatype_cls(self):
#         return datatypes.get(self.datatype)
#
#     def _get_model_cls(self):
#         if self._model_cls is None:
#             self._model_cls = getattr(_models, self.model, None)
#         return self._model_cls
#     model_cls = property(_get_model_cls)
#
#     def _allowed_values_are_valid(self, value):
#         "Boolean check to validate if the allowed_values is the correct format."
#         if type(value) not in ('list', 'tuple'):
#             return False
#         for x in value:
#             if not type(x) in (list, tuple) or len(x) != 2:
#                 return False
#         return True
#
#     def is_valid_model_and_field(self, model, field_name):
#         model_cls = getattr(_models, model, None)
#         if model_cls is None:
#             return False
#         obj = model_cls()
#         return hasattr(obj, field_name)
#
#     def is_valid_graphic_query(self, graphic_query):
#         if not graphic_query:
#             return True
#         conn = psycopg2.connect(**RAW_DB_CONNECTION_SETTINGS)
#         cursor = conn.cursor()
#         try:
#             cursor.execute(graphic_query)
#         except Exception:
#             return False
#         finally:
#             conn.close()
#         return True
#
#     def _set_graphic_attrs(self):
#         json = {}
#
#         # run `graphic_query'
#         from django.db import connection
#         cursor = connection.cursor()
#         cursor.execute(self.graphic_query)
#         rows = cursor.fetchall()
#
#         # sample the rows and determine chart type
#         parsed_rows, chart_type = self.datatype_cls.sample(rows)
#
#         # sort `parsed_rows` based on `allowed_values` if they exist
#         if self.allowed_values:
#             sorted_parsed_rows = []
#             row_values = [x[0] for x in parsed_rows]
#             for val, text in self.allowed_values:
#                 # non-empty set
#                 if val in row_values:
#                     # get index in the row_values
#                     idx = row_values.index(val)
#                     # use same index for parsed_rows. create new tuple
#                     tmp = (text, parsed_rows[idx][1])
#                     sorted_parsed_rows.append(tmp)
#                     # replace text with allowed_values representation
#             parsed_rows = sorted_parsed_rows
#
#         # populates graphic specific attributes
#         json['graphic'] = {
#             'coords': parsed_rows,
#             'type': chart_type,
#             'datatype': self.datatype,
#             'id': self.pk,
#             'title': self.graphic_title,
#             'xaxis': self.graphic_xaxis,
#             'yaxis': self.graphic_yaxis,
#         }
#
#         return json
#
#     def validate(self, operator, value):
#         self.op_obj, self.val_obj = self.datatype_cls.validate(operator, value)
#
#     def save(self):
#         from .cache import field_cache
#         self.modified = datetime.datetime.now()
#         field_cache._build_cache(self)
#         super(Field, self).save()
#
#     def set_allowed_values_fulltext(self):
#         # exclude nulls and the empty string
#         unique_vals_qs = self._model.objects.exclude(
#             Q(**{str(self.field_name+'__isnull'): True}) |
#             Q(**{str(self.field_name): ''})).values_list(
#             self.field_name, flat=True).distinct()
#
#         unique_vals = map(lambda x: str(x), unique_vals_qs)
#
#         val = ', '.join([x.title() for x in unique_vals])
#         self.allowed_values_fulltext = val
#         return val
#
#     @models.permalink
#     def get_absolute_url(self):
#         return 'avocado-render-field', (), {'field_id': self.pk}
#
#     @property
#     def allowed_values(self):
#         """In most cases the `allowed_values` will be an explicit callback or
#         variable defined in the model's namespace. In other cases there may be
#         an implicit set of `allowed_values` derived from the Datatype class.
#         Both cases must be checked prior to setting a value.
#         """
#         if self._allowed_values is not None:
#             return self._allowed_values
#
#         # test to see if `datatype_cls` has a set of choices.
#         if hasattr(self.datatype_cls, 'allowed_values'):
#             self._allowed_values = tuple(self.datatype_cls.allowed_values)
#             return self._allowed_values
#
#         # parse the DB defined callback
#         if self.allowed_values_callback:
#             # try evaling a straight sequence in the format:
#             #   ((1,'foo'), (2,'bar'), ...)
#             try:
#                 choices = eval(self.allowed_values_callback)
#                 if self._allowed_values_are_valid(choices):
#                     self._allowed_values = tuple(choices)
#                     return self._allowed_values
#             except NameError:
#                 pass
#
#             # attempts to check the _model for an attribute `value`:
#             #   when: value = SHAPE_CHOICES
#             #   test: models_class.SHAPE_CHOICES
#             try:
#                 choices = getattr(self.model_cls, self.allowed_values_callback)
#                 if callable(choices):
#                     choices = choices()
#                 self._allowed_values = tuple(choices)
#                 return self._allowed_values
#             except AttributeError:
#                 pass
#
#             # attempts to check the _model' module for an attribute `value`:
#             #   when: value = SHAPE_CHOICES
#             #   test: models_class.__module__.SHAPE_CHOICES
#             try:
#                 mod = __import__(self.model_cls.__module__)
#                 choices = getattr(mod, self.allowed_values_callback)
#                 if callable(choices):
#                     choices = choices()
#                 self._allowed_values = tuple(choices)
#                 return self._allowed_values
#             except AttributeError:
#                 pass
#
#             # try evaling as a Queryset object and iterating over it to create
#             # the choices. the format is:
#             #   ((pk, x.unicode()), ...)
#             try:
#                 qs = eval('%s.%s' % ('_models', self.allowed_values_callback))
#                 if isinstance(qs, ValuesListQuerySet):
#                     choices = qs.distinct()
#                 elif isinstance(qs, QuerySet):
#                     choices = []
#                     for x in qs.iterator():
#                         choices.append((str(x.pk), x.__unicode__()))
#
#                 self._allowed_values = tuple(choices)
#                 return self._allowed_values
#             except TypeError:
#                 pass
#
#             raise ConfigurationError, '%s is not a sequence, constant, ' \
#                 'callable or queryset' % self.allowed_values_callback
#
#     @property
#     def json(self):
#
#         if self._json_cache is not None:
#             return self._json_cache
#
#         json = {'name': self.display_name}
#
#         # set html form
#         from .forms import FieldForm
#         form = FieldForm(self, prefix=u'%s' % self.pk)
#         t1 = get_template('avocado/fields/form.html')
#         c1 = Context({'forms': [(self.pk, form)]})
#         json['form'] = t1.render(c1)
#
#         # set html description
#         t2 = get_template('avocado/fields/description.html')
#         c2 = Context({'object': self})
#         json['description'] = t2.render(c2)
#
#         # set graphic details if exist
#         if self.graphic_query:
#             json.update(self._set_graphic_attrs())
#
#         self._json_cache = simplejson.dumps(json)
#
#         return self._json_cache
#
#     # # DEPRECATED use the FieldForm class directly
#     # @property
#     # def form_class(self):
#     #     "Dynamically generate a Form object representing this Field."
#     #     if self._form_class is None:
#     #         raise DeprecationWarning, 'use the FieldForm class directly'
#     #         self._form_class = FieldForm
#     #     return self._form_class
#
