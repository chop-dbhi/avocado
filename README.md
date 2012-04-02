Avocado
=======
Metadata APIs for Django

- The `DataField` model supplements Django model fields with descriptive
and administrative metadata
    - Includes APIs for fetching data for the particular data field
- The `DataConcept` model associates multiple data fields together for
representation
    - To support this feature, the [ModelTree](https://github.com/cbmi/modeltree)
    API is used for dynamically setting up joins

Design Musing
-------------
The most natural and simplest way to search for information is using natural
language to describe it. This is seen in how Web search engines interfaces
are presented. By using various _key_ words, the search engine can determine the
best match and present Web page results.

Do you know how the search engine came to that conclusion? No, it doesn't matter.
All that matters is that you found the information you were looking for. In order
for a search engine to succeed, it must take the input keywords and find the
relevant Web pages by using various NLP algorithms of varying complexity.

Avocado has a similar goal in that information retrieval should be transparent.
The difference? Web pages are virtually big blobs of text, semantic markup and
metadata. Discrete data have natural constraints based on their datatype, the
contents of the data itself, and how the data is stored (e.g. relational database).

The one advantage of discrete data is the ability to control what data you see
once the information is retrieved. Discrete data also enables creating explicit
interfaces showing off what data is available.

Desired APIs
------------

```python
# Get the 'book title' data field
book_title = DataField.objects.get(model_name='book', field_name='title')

# Get the 'book' concept. A DataConcept is composed of one or more data fields
# intended to be representated together in some way.
book_concept = DataConcept.objects.get(name='Book')

dickens = Author.objects.get(name='Charles Dickens')

# Get all book titles related to the author object
book_title.get_data_for(dickens)
['Pickwick Papers', 'Oliver Twist', 'Nicholas Nickleby', ...]

# This concept combines the title, publication year and the author's
# name. All book data related to the author 'Charles Dickens' will
# be retrieved.
book_concept.get_data_for(dickens)
[
    {'title': 'Pickwick Papers', 'publication_year': 1836, 'author': 'Charles Dickens'},
    {'title': 'Oliver Twist', 'publication_year': 1838, 'author': 'Charles Dickens'},
    {'title': 'Nicholas Nickleby', 'publication_year': 1839, 'author': 'Charles Dickens'},
    ...
]

# Concepts also provide a formatter API for representing the data in
# non-raw formats
book_concept.get_data_for(dickens, preferred_formats=['html'])
[
    '<h1>Pickwick Papers</h1><br><strong>Published in 1836 by Charles Dickens</strong>',
    '<h1>Oliver Twist</h1><br><strong>Published in 1838 by Charles Dickens</strong>',
    '<h1>Nocholas Nickleby</h1><br><strong>Published in 1839 by Charles Dickens</strong>',
    ...
]
```
