# For custom translators, this is the name of the module that will be 
# introspected per app for registered translators
TRANSLATOR_MODULE_NAME = 'translate'

# Defines an abstract base class to extend the Field model. It should be
# ``None`` or a path string to the class e.g. 'path.to.my.field.Mixin'
FIELD_MIXIN_PATH = None

# For custom formatters, this is the name of the module that will be
# introspected per app for registered formatters
FORMATTER_MODULE_NAME = 'format'

# A definition for customizing the ``Column`` model. Each key in the dict will
# be the name of the column formatter type as well as the name of the model
# field name (with FORMATTER_FIELD_SUFFIX). These correspond to the output
# formats produced by the column formatter library
FORMATTER_TYPES = {}

# The formatter type field suffix, e.g. given a formatter type 'csv', the
# field that will be added to the ``Column`` model will be called 'csv_fmt'
FORMATTER_FIELD_SUFFIX = '_fmtr'

# A tuple of ``Column`` ids that represents the default ordering for reports
COLUMN_ORDERING = ()

# A tuple of ``Column`` ids that represents the default columns to be shown
# in a report
COLUMNS = ()

# Defines an abstract base class to extend the Column model. It should be
# ``None`` or a path string to the class e.g. 'path.to.my.column.Mixin'
COLUMN_MIXIN_PATH = None

# For custom viewsets, this is the name of the module that will be
# introspected per app for registered viewsets
VIEWSET_MODULE_NAME = 'viewset'

# Defines an abstract base class to extend the Criterion model. It should be
# ``None`` or a path string to the class e.g. 'path.to.my.criterion.Mixin'
CRITERION_MIXIN_PATH = None

# A dict of modeltree configurations. Each config should contrain the necessary
# keyword args for constructing a default ``ModelTree`` instance. View the 
# ``ModelTree`` docs for potential arguments
MODELTREES = {}
