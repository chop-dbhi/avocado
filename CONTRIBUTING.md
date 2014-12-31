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

- If you do not have write access to the repo (i.e. not a core contributor), create a fork
- Branches are used to isolate development and ensure clear and concise intent of the code.
- Always do your work in a branch off the `master` branch.
- Leave a comment on the issue you want to work on to get a conversation started.
- Issues marked with [status:help-wanted](https://github.com/chop-dbhi/avocado/labels/status%3Ahelp-wanted) are isolated issues that are good for new contributors.
- Or, [create a new issue](https://github.com/chop-dbhi/avocado/issues/) if you have a question or idea.
- Name the branch after the issue number you are working on, e.g. `issue-123`.
- Ensure the coding style matches the code in the repository. Consult our [style guides](https://github.com/chop-dbhi/style-guides/) if you are unsure.

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
