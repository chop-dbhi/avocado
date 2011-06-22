Data Exporter API
=================

Avocado has support for exporting data in various formats including:

    * CSV
    * Tab-delimited
    * Microsoft Excel
    * SAS
    * R
    * XML
    * JSON

The challenge with exporting data is formatting the data appropriate for
intended client, whether human or machine. Certain formats have some notion
or syntax for datatypes (i.e. JSON) while others do not (i.e. CSV). Therefore
the job of the any given exporter is to define a list of preferred formats
data should be represented.

The interface between the Exporter and the data are the Concepts. Every piece
of data has a Concept (and thus a Definition) associated with it. A Concept has
the option of specifying a custom ``Formatter`` class for the associated data.

The ``Formatter`` class has the job of formatting, coercing, mapping, etc. the
raw data depending on the client's (the Exporter in this case) preference.

The high-level workflow is as follows:

    1. A client requests a JSON export of the current report
    2. A sequence of formatting rules are created given the Concepts
       representing the data
    3. Each data row is fetched passed through the formatters
    4. The Exporter incrementally builds the file and streams the data
       to the client 

