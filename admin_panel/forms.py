"""ModelForms backing every create/update screen in the custom admin.

The old panel bound request.POST straight to model constructors, so bad input
either 500'd or saved half-empty rows. These forms give the same fields proper
validation, error rendering and file handling while keeping the exact model
field names the public templates already rely on.
"""

from ckeditor.widgets import CKEditorWidget
from django import forms

from blog.models import Blog_Post
from portfolio.models import (
    Client_Logo,
    Post_Design,
    Pricing_Plan,
    Print_Design,
    Testimonial,
    Website_Portfolio,
)

TEXT = {'class': 'bh-input'}
TEXT_SMALL = {'class': 'bh-input', 'rows': 3}
FILE = {'class': 'bh-file', 'accept': 'image/*'}
URL = {'class': 'bh-input', 'placeholder': 'https://example.com'}


class BlogPostForm(forms.ModelForm):
    """Post editor.

    Every model here treats its image as optional, so leaving the file input
    empty keeps whatever is already stored. The ``clear_image`` checkbox on the
    models that have one is the only way to clear a file, which stops an
    accidental empty submit from wiping     a thumbnail that is live on the site.
    """

    clear_image = forms.BooleanField(
        required=False,
        label='Remove current image',
        widget=forms.CheckboxInput(attrs={'class': 'bh-check'}),
    )
    # Model fields are CharFields, so the URLInput widget alone would validate
    # nothing — declare the field itself.
    author_profile_link = forms.URLField(
        required=False,
        assume_scheme='https',
        widget=forms.URLInput(attrs={**URL, 'placeholder': 'https://linkedin.com/in/…'}),
    )

    class Meta:
        model = Blog_Post
        fields = [
            'title',
            'category',
            'author',
            'about_author',
            'author_profile_link',
            'image',
            'content',
            'meta_description',
            'is_published',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={**TEXT, 'placeholder': 'e.g. Why your brand needs a custom website'}
            ),
            'category': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Web Design'}),
            'author': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Rahim Uddin'}),
            'about_author': forms.Textarea(
                attrs={**TEXT_SMALL, 'placeholder': 'Short bio shown under the post'}
            ),
            'author_profile_link': forms.URLInput(
                attrs={**URL, 'placeholder': 'https://linkedin.com/in/…'}
            ),
            'image': forms.FileInput(attrs=FILE),
            'content': CKEditorWidget(),
            'meta_description': forms.Textarea(
                attrs={
                    **TEXT_SMALL,
                    'placeholder': 'Shown as the page description in search results.',
                }
            ),
            'is_published': forms.CheckboxInput(attrs={'class': 'bh-check'}),
        }

    def clean_title(self):
        title = (self.cleaned_data.get('title') or '').strip()
        if not title:
            raise forms.ValidationError('A title is required.')
        return title

    def clean_meta_description(self):
        value = (self.cleaned_data.get('meta_description') or '').strip()
        if len(value) > 160:
            raise forms.ValidationError(
                'Keep this under 160 characters or search engines will truncate it.'
            )
        return value


class WebsitePortfolioForm(forms.ModelForm):
    clear_image = forms.BooleanField(
        required=False,
        label='Remove current image',
        widget=forms.CheckboxInput(attrs={'class': 'bh-check'}),
    )
    link = forms.URLField(
        assume_scheme='https',
        widget=forms.URLInput(attrs={**URL, 'placeholder': 'https://example.com'}),
    )

    class Meta:
        model = Website_Portfolio
        fields = ['title', 'category', 'technology', 'link', 'image']
        widgets = {
            'title': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Aurora Fashion Hub'}),
            'category': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. E-Commerce'}),
            'technology': forms.TextInput(
                attrs={**TEXT, 'placeholder': 'e.g. Django, Tailwind, PostgreSQL'}
            ),
            'link': forms.URLInput(attrs={**URL, 'placeholder': 'https://example.com'}),
            'image': forms.FileInput(attrs=FILE),
        }


class PrintDesignForm(forms.ModelForm):
    clear_image = forms.BooleanField(
        required=False,
        label='Remove current image',
        widget=forms.CheckboxInput(attrs={'class': 'bh-check'}),
    )

    class Meta:
        model = Print_Design
        fields = ['title', 'image']
        widgets = {
            'title': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Eid Sale Banner'}),
            'image': forms.FileInput(attrs=FILE),
        }


class PostDesignForm(forms.ModelForm):
    clear_image = forms.BooleanField(
        required=False,
        label='Remove current image',
        widget=forms.CheckboxInput(attrs={'class': 'bh-check'}),
    )

    class Meta:
        model = Post_Design
        fields = ['title', 'image']
        widgets = {
            'title': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Instagram launch post'}),
            'image': forms.FileInput(attrs=FILE),
        }


class TestimonialForm(forms.ModelForm):
    clear_image = forms.BooleanField(
        required=False,
        label='Remove current image',
        widget=forms.CheckboxInput(attrs={'class': 'bh-check'}),
    )

    class Meta:
        model = Testimonial
        fields = ['title', 'content', 'image']
        widgets = {
            'title': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Sarah Islam, Founder'}),
            'content': forms.Textarea(
                attrs={**TEXT_SMALL, 'placeholder': 'What the client said about working with you.'}
            ),
            'image': forms.FileInput(attrs=FILE),
        }

    def clean_content(self):
        content = (self.cleaned_data.get('content') or '').strip()
        if len(content) > 400:
            raise forms.ValidationError('Trim this to 400 characters so it fits the homepage card.')
        return content


class ClientLogoForm(forms.ModelForm):
    clear_image = forms.BooleanField(
        required=False,
        label='Remove current logo',
        widget=forms.CheckboxInput(attrs={'class': 'bh-check'}),
    )
    link = forms.URLField(
        required=False,
        assume_scheme='https',
        widget=forms.URLInput(attrs={**URL, 'placeholder': 'https://example.com (optional)'}),
    )

    class Meta:
        model = Client_Logo
        fields = ['title', 'link', 'image']
        widgets = {
            'title': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Aurora Fashion'}),
            'link': forms.URLInput(
                attrs={**URL, 'placeholder': 'https://example.com (optional)'}
            ),
            'image': forms.FileInput(attrs=FILE),
        }
        help_texts = {
            'image': 'Transparent PNG works best, roughly 400 x 110 px.',
            'link': 'Leave empty if this client has no site to link to.',
        }


class PricingPlanForm(forms.ModelForm):
    """A price tier on the homepage.

    ``features`` is a plain textarea with one bullet per line — the public
    template splits it — so an editor never edits markup directly. ``price`` is
    a text field on purpose (see the model) and ``cta_link`` is optional; when
    left empty the public card falls back to the contact page.
    """

    class Meta:
        model = Pricing_Plan
        fields = [
            'title',
            'tagline',
            'price',
            'period',
            'description',
            'features',
            'cta_text',
            'cta_link',
            'is_featured',
            'is_active',
            'order',
        ]
        widgets = {
            'title': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Starter'}),
            'tagline': forms.TextInput(
                attrs={**TEXT, 'placeholder': 'e.g. For small businesses getting online'}
            ),
            'price': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. 499 or Custom'}),
            'period': forms.TextInput(
                attrs={**TEXT, 'placeholder': 'e.g. /project or /month (optional)'}
            ),
            'description': forms.Textarea(
                attrs={**TEXT_SMALL, 'placeholder': 'One or two lines about this plan.'}
            ),
            'features': forms.Textarea(
                attrs={**TEXT_SMALL, 'rows': 6, 'placeholder': 'One feature per line…'}
            ),
            'cta_text': forms.TextInput(attrs={**TEXT, 'placeholder': 'e.g. Get started'}),
            'cta_link': forms.TextInput(
                attrs={**TEXT, 'placeholder': 'https://example.com or /contact_us/ (optional)'}
            ),
            'is_featured': forms.CheckboxInput(attrs={'class': 'bh-check'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'bh-check'}),
            'order': forms.NumberInput(attrs={**TEXT, 'min': 0}),
        }
        help_texts = {
            'features': 'One feature per line — each becomes a bullet on the card.',
            'period': 'Shown small next to the price, e.g. “/project”.',
            'order': 'Lower numbers appear first.',
            'price': 'A plain number gets the ৳ (BDT) symbol added automatically.',
        }

    def clean_features(self):
        return (self.cleaned_data.get('features') or '').strip()

    def clean_cta_text(self):
        return (self.cleaned_data.get('cta_text') or '').strip() or 'Get started'


class ContactSearchForm(forms.Form):
    """GET-side filter for the inbox. Kept as a form so the query string and
    the inputs can never drift apart."""

    q = forms.CharField(required=False, label='Search')
    state = forms.ChoiceField(
        required=False,
        label='State',
        choices=[('unread', 'Unread'), ('read', 'Read'), ('all', 'All')],
    )
