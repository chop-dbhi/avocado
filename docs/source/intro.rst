Introduction
============

The origin of avocado sprouted from within the research community to provides a
means of asking very arbitrary questions about data. Since it is research,
standard questions either have not been established yet or do not make up the
majority of questions being asked for the particular knowledge domains.

Avocado provides meta-programming APIs to facilitate asking arbitrary
questions about the data of interest. Research data may span multiple
domains of knowledge and may have several hundred discrete data fields
associated with the data model. The depth of the relationships between the
data fields may go beyond what is practical to merely statically code up.
In a nutshell, avocado allows for asking arbitrary questions at runtime.

What do I mean by *question*?
-----------------------------

A question in this context (i.e. programming) virtually maps to a SQL query.
Thus, if one is capable of constructing a SQL query to ask a particular
question, they will also be able to construct the same question using avocado.

What's the advantage? People who do not know what SQL is, or those who do, but
not the intricacies of the language, would not be able to ask there question
without having a SQL expert to consult.

What do I mean *at runtime*?
----------------------------

A typical way researchers "ask" questions is by getting a SQL data dump with
tons of information, then attempt to filter and anaylyze the data in a
spreadsheet. This can be very time consuming and the spreadsheet quickly
becomes difficult to manage and maintain.

The other big problem? You are restricted to that data. What happens if you
are honing in on the question you ultimately should be asking, but now
don't have all the necessary data? You have to go to talk to that SQL expert
again. The process becomes tedious.

Being able to ask any question at any time is quite convenient. Implementing
this feature programmatically can be thought as being able to "ask questions
at runtime", runtime meaning *on-the-fly*. 

Avocado uses the Django Object-Relational Mapping (ORM) API to incrementally
build SQL queries. Again, the problem here is needing to know what queries to
construct ahead of time. Avocado provides an API to write server and/or client
applications to present the queryable fields in a non-relational way to the
end-user. The end-user should not have to know how your data model is put
together; they simply want to ask questions about the data.

