# Contributing

First off, thank you for considering a contribution!

Before you submit any code, please read the following Developer's Certificate of Origin (DCO):

```
By making a contribution to the Avocado project ("Project"),
I represent and warrant that:

a. The contribution was created in whole or in part by me and I have the right
to submit the contribution on my own behalf or on behalf of a third party who
has authorized me to submit this contribution to the Project; or

b. The contribution is based upon previous work that, to the best of my
knowledge, is covered under an appropriate open source license and I have the
right and authorization to submit that work with modifications, whether
created in whole or in part by me, under the same open source license (unless
I am permitted to submit under a different license) that I have identified in
the contribution; or

c. The contribution was provided directly to me by some other person who
represented and warranted (a) or (b) and I have not modified it.

d. I understand and agree that this Project and the contribution are publicly
known and that a record of the contribution (including all personal
information I submit with it, including my sign-off record) is maintained
indefinitely and may be redistributed consistent with this Project or the open
source license(s) involved.
```

This DCO simply certifies that the code you are submitting abides by the clauses stated above. To comply with this agreement, all commits must be signed off with your legal name and email address.

## Logistics

- If you do not have write access to the repo (i.e. not a core contributor), create a fork of Avocado
- Branches are used to isolate development and ensure clear and concise intent of the code. Always do your work in a branch off the `master` branch. This will be a mirror of the work-in-progres (WIP) branch for the current major version, e.g. `2.x`. Name the branch after the issue and number, e.g. `issue-123`. If there is no issue number, [please create one first](https://github.com/cbmi/avocado/issues/) before starting your work.
- If working on existing files, ensure the coding style is kept consistent with the code around it. If creating new files or you are unsure of a pattern or preference please consult the [style guides](https://github.com/cbmi/style-guides/) for the applicable language.

## Testing

Pre-requisite for testing:

- memcached running on 127.0.0.1:11211

Install test dependencies:

```
pip install -r requirements.txt
```

Run the test suite:

```
python test_suite.py
```
