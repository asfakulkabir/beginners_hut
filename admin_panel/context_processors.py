"""Context shared by every admin screen.

The sidebar shows an unread-count badge and a draft count next to the two
links that gain meaning over time, which would otherwise mean repeating the
same COUNT query in every view just to render the chrome.
"""

from blog.models import Blog_Post
from portfolio.models import Contact


def admin_chrome(request):
    user = getattr(request, 'user', None)
    if not (user and user.is_authenticated and user.is_superuser):
        return {}

    return {
        'bh_unread': Contact.objects.filter(is_read=False).count(),
        'bh_drafts': Blog_Post.objects.filter(is_published=False).count(),
        'bh_in_admin': True,
    }
