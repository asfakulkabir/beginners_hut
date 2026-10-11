from django.db import models
from django.utils import timezone


class Website_Portfolio(models.Model):
    category= models.CharField(max_length=900)
    title= models.CharField(max_length=900)
    technology= models.CharField(max_length=900)
    link= models.CharField(max_length=900)
    image = models.ImageField(upload_to='upload/website_thumbnail',blank=True,default=None)

    def __str__(self) -> str:
        return self.title

    @property
    def group(self):
        """Canonical service bucket used by the portfolio filter UI.

        The raw `category` values are free text and inconsistent
        ('E-Commerce', 'E-COmmerce', 'E-commerce', 'Dropshipping', ...), so
        they are normalised into one of five stable keys. Order matters:
        software is checked before commerce, and commerce before the
        catch-all website bucket.
        """
        c = (self.category or '').strip().lower()
        if 'software' in c or 'pos' in c:
            return 'software'
        if any(k in c for k in ('commerce', 'dropshipping', 'vendor', 'shop', 'store')):
            return 'ecommerce'
        return 'website'

    @property
    def group_label(self):
        return {
            'website': 'Website',
            'software': 'Software',
            'design': 'Graphics',
            'ecommerce': 'E-Commerce',
            'video': 'Video',
        }.get(self.group, 'Website')

    @property
    def tech_list(self):
        """Technology field -> clean list of tags."""
        if not self.technology:
            return []
        parts = self.technology.replace('&', ',').split(',')
        return [p.strip() for p in parts if p.strip()]

class Print_Design(models.Model):
    title= models.CharField(max_length=900)
    image = models.ImageField(upload_to='upload/print_design',blank=True,default=None)

    def __str__(self) -> str:
        return self.title

class Post_Design(models.Model):
    title= models.CharField(max_length=900)
    image = models.ImageField(upload_to='upload/post_design',blank=True,default=None)

    def __str__(self) -> str:
        return self.title

class Testimonial(models.Model):
    title= models.CharField(max_length=900)
    content= models.CharField(max_length=900)
    image = models.ImageField(upload_to='upload/testimonial_logo',blank=True,default=None)

    def __str__(self) -> str:
        return self.title

class Client_Logo(models.Model):
    """Logo shown in the homepage 'Trusted by' marquee.

    Logos are rendered at a fixed 160x44 CSS box with object-contain, so
    anything uploaded here lines up with everything else regardless of its
    pixel dimensions. The recommended upload is 400x110 (2x for retina) with a
    transparent background — the admin form states this and warns when the
    file's real dimensions are far off.
    """
    title = models.CharField(max_length=900)
    image = models.ImageField(upload_to='upload/client_logo', blank=True, default=None)
    link = models.CharField(max_length=900, blank=True, default='')

    def __str__(self) -> str:
        return self.title

    @property
    def target_url(self):
        """Website URL, normalised so it is safe to put in an href."""
        url = (self.link or '').strip()
        if not url:
            return ''
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
        return url


class Pricing_Plan(models.Model):
    """A price tier shown in the homepage 'Pricing' section.

    ``price`` is free text ('$499', 'From $80/hr', 'Custom') rather than a
    DecimalField: quotes are not always a single number, and forcing a numeric
    price would make 'Custom' or 'POA' impossible to enter. ``features`` is one
    bullet per line so an editor never has to touch markup.
    """

    title = models.CharField(max_length=200)
    tagline = models.CharField(max_length=300, blank=True, default='')
    price = models.CharField(max_length=100)
    period = models.CharField(max_length=60, blank=True, default='')
    description = models.TextField(blank=True, default='')
    features = models.TextField(blank=True, default='')
    cta_text = models.CharField(max_length=100, blank=True, default='Get started')
    cta_link = models.CharField(max_length=300, blank=True, default='')
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self) -> str:
        return self.title

    @property
    def feature_list(self):
        """``features`` -> clean list of bullets, blank lines dropped."""
        return [line.strip() for line in (self.features or '').splitlines() if line.strip()]

    @property
    def shows_currency_prefix(self):
        """True when the price is a bare number, so the template can prefix the
        Bangladeshi Taka sign (৳). Text prices like 'Custom' are left untouched."""
        price = (self.price or '').strip()
        return bool(price) and price[0].isdigit()

    @property
    def target_url(self):
        """CTA link normalised so it is safe in an href, or '' when unset."""
        url = (self.cta_link or '').strip()
        if not url:
            return ''
        if not url.startswith(('http://', 'https://', '/')):
            url = 'https://' + url
        return url


class Contact(models.Model):
    mail = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.CharField(max_length=1000)
    time = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-time', '-id']

    def __str__(self) -> str:
        return self.mail

    def mark_read(self):
        if self.is_read:
            return False
        self.is_read = True
        self.read_at = timezone.now()
        self.save(update_fields=['is_read', 'read_at'])
        return True

    def mark_unread(self):
        if not self.is_read:
            return False
        self.is_read = False
        self.read_at = None
        self.save(update_fields=['is_read', 'read_at'])
        return True