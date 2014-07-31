from django.test import TestCase
from django.contrib.auth.models import User
from avocado.core import utils


class EmailBasedUserTestCase(TestCase):
    email = 'email@email.com'

    def test_create_user(self):
        # Make sure we are starting with the anticipated number of users.
        self.assertEqual(User.objects.count(), 1)

        user = utils.create_email_based_user(self.email)

        self.assertEqual(User.objects.count(), 2)

        # Make sure the user we got back has the correct email set and that
        # they are not active.
        self.assertEqual(user.email, self.email)
        self.assertFalse(user.is_active)
