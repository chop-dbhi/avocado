from django.db import models
from avocado.lexicon.models import Lexicon


class Month(Lexicon):
    label = models.CharField(max_length=20)
    value = models.CharField(max_length=20)
