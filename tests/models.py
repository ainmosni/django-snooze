from django.db import models


class Simple(models.Model):
    """
    Simple test model.
    """

    one = models.IntegerField()
    two = models.CharField(max_length=20)

    def __unicode__(self):
        return '{}/{}'.format(self.one, self.two)
