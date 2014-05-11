from django.db import models


class Simple(models.Model):
    """
    Simple test model.
    """

    one = models.IntegerField()
    two = models.CharField(max_length=20, default='spam')

    def __unicode__(self):
        return '{}/{}'.format(self.one, self.two)


class Abstract(models.Model):
    """
    Abstract test model.
    """

    one = models.IntegerField()
    two = models.CharField(max_length=20, default='eggs')

    def __unicode__(self):
        return '{}/{}'.format(self.one, self.two)

    class Meta:
        abstract = True
