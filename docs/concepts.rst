The Concept Behind "Concepts"
=============================

In ``avocado.concepts.models`` lives the abstract ``Concept`` model. Metadata
is equally about describing a data model as it is providing the tools to
discover and/or utilize this metadata. The ``Concept`` model has a single
required field, ``name``, which must be unique. This is not a technical
constraint as much as it is a good practice to follow. Whether this metadata
is being used by the implementers or by the end-users, being unambiguous about
the data model is important for ease of interpretation.

To facilitate knowledge and discovery, attributes such as ``description``,
``keywords``, and ``category`` provides a means of describing what a particular
concept represents within the context of the data model. As you will see in a
second, a concept need not be a one-to-one with a single field in the data
model. This is hence the terminology "concept",

