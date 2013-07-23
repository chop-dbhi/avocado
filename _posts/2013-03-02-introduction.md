---
layout: page
title: "Introduction"
category: doc
date: 2013-03-02 08:38:03
order: 0
---

## Target Audience

**Developers who are interested in letting their data do the work for them.**

#### Before you begin:
- Some general Python experience is necessary.
- Some experience with Django is necessary. If you are unfamiliar with Django, the [tutorial](https://docs.djangoproject.com/en/1.4/intro/tutorial01/) is an excellent place to start, or you can look into the [model docs](https://docs.djangoproject.com/en/1.4/topics/db/models/). 

## Background

Django models provides the **structural** metadata necessary for interfacing with the supported database backends. However, in general, there is no formal mechanism to supply **descriptive** or **administrative** metadata about your data model. Avocado is a Django app which provides easy metadata management for your models.

Avocado grew out of projects developed in a clinical research environment, where data models are frequently very large and complex. Additionally in this setting, there are data fields that contain related but decoupled data. This typically results in a large hierarchical data model, which can get pretty messy pretty quickly.

When developing applications that make use of this type of data, developers need to be able to provide end-users with appropriate context and representation of the data elements to avoid confusion and errors of omission.

### A Real Example

All this abstract talk can be a bit confusing, so lets jump into an example. In medicine, it's typical that results from a diagnostic test like a blood test might be broken into several columns in a relational database: a numerical value, units of measure, and an assessment as to whether it is normal, high, or low. As a developer you'd like to be able to bundle these conveniently in your application.

While you could just store them all as one text field in your database, that sacrifices the ability to query and perform mathematical calculations on the numerical field. On the other hand, splitting them apart means a user who does not know your data model very well needs to know upfront to hunt down the various elements on their own, or they risk getting an incomplete picture of the retrieved data.

In many cases, these kinds of complexities result in a research workflow where the technical team act as "keepers of the data", and all the researcher's questions are filtered through them to be translated into queries. This situation, while good for the continued employment of engineers, is not ideal for open-ended discovery and hypothesis generation by researchers.

### The Solution

Avocado was designed to support the development of accessible, transparent, and data-rich applications by providing several capabilities:

- A formal way to store additional metadata for your data model
- Robust API's for interrogating metadata for dynamic query generation which includes translation, validation, cleaning, and execution of queries
- Built-in extensible components for the formatting and exporting of data

The power of Avocado's dynamic query generation lies in it's ability to [span relationships transparently](#relationships-are-transparent). This allows users (and to some extent developers) to focus on the data and not have to worry about the data model.

### Target Applications

While Avocado can be useful for any project, it is most likely applicable to projects with a heavy focus on data. As a developer, it can be very useful as a tool for _accessing_ some data for the first time. For users, it is most useful for applications focused on domain-specific data discovery.

### Next: [Installation & Setup]({{ site.baseurl }}{% post_url 2013-06-06-installation-setup %})
