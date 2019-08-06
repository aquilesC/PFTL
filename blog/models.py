from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.html import strip_tags

from blog.conf import POST_STATE_CHOICES
from blog.managers import PostManager


class Section(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True)
    enabled = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    section = models.ForeignKey(Section, on_delete=models.CASCADE)

    title = models.CharField(max_length=90, null=False, blank=False)
    slug = models.SlugField(max_length=90, unique=True)

    content = models.TextField()
    excerpt = models.TextField(blank=True)

    excerpt_html = models.TextField(editable=False)
    content_html = models.TextField(editable=False)

    description = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(null=True, blank=True, editable=False)
    published = models.DateTimeField(null=True, blank=True)

    state = models.IntegerField(choices=POST_STATE_CHOICES, default=POST_STATE_CHOICES[0][0])

    view_count = models.IntegerField(default=0, editable=False)

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    objects = PostManager()

    @property
    def is_published(self):
        return self.state == POST_STATE_CHOICES[-1][0]

    @property
    def meta_description(self):
        if self.description:
            return self.description
        return strip_tags(self.excerpt_html)

    @property
    def older_post(self):
        qs = Post.objects.published()
        if self.is_published:
            qs = qs.filter(published__lt=self.published)
        return next(iter(qs), None)

    @property
    def newer_post(self):
        if self.is_published:
            return next(iter(Post.objects.published().order_by('published').filter(published__gt=self.published)), None)

    class Meta:
        ordering = ('-published', )
        get_latest_by = 'published'

    def __str__(self):
        return self.title

    def save(self, **kwargs):
        self.updated = timezone.now()
        if self.is_published and self.published is None:
            self.published = timezone.now()
        self.full_clean()
        super(Post, self).save(**kwargs)

    def increase_views(self):
        self.view_count += 1
        self.save()


class Comment(models.Model):
    author = models.ForeignKey(User, null=True, related_name='comments', on_delete=models.SET_NULL)

    name = models.CharField(max_length=100)
    email = models.EmailField()
    website = models.URLField()

    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    reply_to = models.ForeignKey('self', related_name='replies', on_delete=models.CASCADE, null=True, default=None)

    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True)

    public = models.BooleanField(default=False)

    def __str__(self):
        return f'Comment from {self.name} on {self.post}'