Domains
=======

The ``Domain`` model represents a very simple way to organize concepts.
::

    >>> proteomics = Domain(name='Proteomics')
    >>> ppi = Concept(name='Protein-Protein Interaction', ...)
    >>> ppi.domain = proteomics

Domains can also be nested (i.e. sub-domains) by simply defining the
``parent`` domain.
::

    >>> bioinformatics = Domain(name='Bioinformatics')
    >>> proteomics.parent = bioinformatics

.. note::

    For easier management and clarity, a concept can only be associated to a
    single domain.
