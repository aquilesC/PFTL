from django.db import models
from django.utils import timezone

from blog.conf import POST_STATE_CHOICES


class PostManager(models.Manager):
    def published(self):
        return self.filter(published__lte=timezone.now(), state=POST_STATE_CHOICES[-1][0])