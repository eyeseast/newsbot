import datetime
from django.db import models
from django.template.defaultfilters import slugify

from calais import Calais
from datutil import parser
from model_utils import Choices
from model_utls.managers import manager_from
from model_utils.models import TimeStampedModel
from taggit.managers import TaggableManager

if hasattr(settings, 'CALAIS_API_KEY'):
    calais = Calais(settings.CALAIS_API_KEY)
else:
    calais = None

# managers

# models

class Source(TimeStampedModel):
    """
    A source of news, like the Washington Post
    """
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    url = models.URLField(help_text="This outlet's main URL")
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return unicode(self.name)


class Feed(TimeStampedModel):
    """
    An RSS or ATOM feed, attached to a Source with a URL
    that can be parsed by feedparser.parse
    """
    FORMAT_CHOICES = Choices(
        ('rss', 'RSS'),
        ('atom', 'ATOM'),
    )
    
    source = models.ForeignKey(Source, related_name='feeds')
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    url = models.URLField(max_length=255, unique=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, 
        default=FORMAT_CHOICES.rss)
    
    class Meta:
        ordering = ('source', 'name')
    
    def __unicode__(self):
        return u"%s: %s" % (self.source.name, self.name)


class EntityType(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return unicode(self.name)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(EntityType, self).save(*args, **kwargs)


class Entity(TimeStampedModel):
    """
    An entity found in a news story
    """
    type = models.ForeignKey(EntityType, related_name='entities')
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return unicode(self.name)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Entity, self).save(*args, **kwargs)
    

class FeedItem(TimeStampedModel):
    """
    An item in a feed
    """
    source = models.ForeignKey(Source, related_name='items')
    feed = models.ForeignKey(Feed, related_name='items')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255)
    date = models.DateTimeField(default=datetime.datetime.now)
    link = models.URLField(unique=True)
    summary = models.TextField(blank=True)
    content = models.TextField()
    tags = TaggableManager(blank=True)
    
    # internal bits
    is_full_text = models.BooleanField(default=True)
    public = models.BooleanField(default=True)
    allow_comments = models.BooleanField(default=False)
    
    class Meta:
        get_latest_by = "date"
        ordering = ('-date',)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super(FeedItem, self).save(*args, **kwargs)
