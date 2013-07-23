---
layout: page
title: "Translators"
category: doc
date: 2013-06-09 13:17:34
---

### Field Translator

Translators are useful for converting values before querying the database. Say for instance that we want to be able to query our database based on a patient age, but we are only storing the patients date of birth. We can write a translator to convert the patient age to the appropriate birthdate to get the correct results from the query.

Translators are used to modify query conditions prior to being executed. Depending on the quality or variability of your data, the query interface for a field may be a simplified representation to the underlying data. Thus the incoming query condition may need to be translated in some way to work with the underlying database.


These operator classes perform only light validation of the value to prevent being too restrictive.

```python
>>> from avocado.query.operators import registry as operators
>>> iexact = operators.get('iexact')
>>> iexact.is_valid(['hello', 'world'])
False
>>> iexact.is_valid('hello world')
True
>>> inlist = operators.get('inlist')
>>> inlist.is_valid(['hello', 'world'])
True
>>> inlist.is_valid('hello world')
False
```

The base `Translator` class uses [Django's Form API](https://docs.djangoproject.com/en/1.4/ref/contrib/forms/api/) to validate and clean the value relative to the underlying model field (e.g. `f.field`).

The primary method to call is `translate` which calls `clean_value` and `clean_operator`.

```python
>>> from avocado.query.translators import Translate
>>> from avocado.models import DataField
>>> f = DataField.objects.get('library', 'book', 'title')
>>> t = Translator()
>>> t.translate(f, 'icontains', 'Python')
{
    'id': 2,
    'operator': 'icontains',
    'value': 'Python',
    'cleaned_data':{
        'operator': <Operator: "contains the text" (icontains)>,
        'value': u'Python',
        'language': u'Book title contains the text Python',
    }
    'query_modifiers':{
        'condition': <django.db.query_utils.Q at 0x1027b78d0>,
        'annotations': None,
        'extra': None 
    }
}
```

### Concept Translator

A translator can also be defined at the Concept-level. Although rare, this provides additional control over how fields get translated together if the need arises.

The `Concept` model also defines a convenience method for translating query conditions. In the example below, the data model contains a model `Cohort` represents a set of samples whose genetic variants have been aggregated together to determine the _allele frequency_ within the cohort. For example, if 5 of 50 samples contains the allele `G` at position `2,932,415` on chromosome `3`, the allele frequency would be `0.1`.

For variant analysis, it is common to filter out _common variants_ relative to one or more control populations (samples known _not_ to have the disease of interest). However, if a naive filter is applied to "include all variants that exist a cohort A with an allele frequency lower than X" is that any variants _not_ present in that cohort will also be excluded since the join constrains the data set to limit the cohort.

What we really want is, "include all variants that exist in cohort A with an allele frequency greater than x **OR** the variant is not in cohort A". This prevents excluding variants not present in the cohort.

In order to do this, a Concept can be defined that includes two fields: _Cohort Name_ and _Cohort Variant Allele Frequency_. We then define a translator that constructs the condition to our liking.

```python
from avocado.query.translators import Translator

class CohortTranslator(Translator):
    def translate_concept(self, concept, fields, operator, tree, **kwargs):
        # Ensure both fields are present, otherwise return none to prevent
        # translation at this level
        if len(fields) != 2:
            return

        # Parsed field nodes conditions
        name = nodes['cohort.name'].condition
        af = nodes['cohortvariant.af'].condition

        # Desired condition
        condition = (name & af) | ~name

        return {
            'condition': condition,
            'annotations': None,
            'extra': None,
        }

```
