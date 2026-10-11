from django.shortcuts import render, redirect
from django.contrib import messages
from .models import *
from blog.models import *


# Number of graphics items folded into the unified portfolio grid.
# Post designs are numerous and repetitive, so only the newest ones are shown.
GRAPHICS_POST_LIMIT = 12

# Deterministic placeholder rotation used when an item has no uploaded image.
PLACEHOLDER_TONES = 6


def build_portfolio_items(website_portfolio, print_design, post_design):
    """Merge the three work models into one list of uniform dicts.

    The homepage portfolio grid needs a single shape for every card so the
    filter chips and load-more behave predictably. Each dict carries:
      group       -> filter bucket (website | software | ecommerce | design | video)
      group_label -> human readable badge text
      title       -> card heading
      meta        -> supporting line (technology or category)
      tech        -> list of tags
      link        -> external project URL (may be empty)
      image       -> media URL, or None when nothing is uploaded
      placeholder -> fallback placeholder filename when image is missing
      kind        -> "web" | "print" | "post"
    """
    items = []

    for w in website_portfolio:
        items.append({
            'group': w.group,
            'group_label': w.group_label,
            'title': w.title,
            'meta': (w.category or '').strip(),
            'tech': w.tech_list,
            'link': (w.link or '').strip(),
            'image': '/media/%s' % w.image if w.image else None,
            'kind': 'web',
        })

    for p in print_design:
        items.append({
            'group': 'design',
            'group_label': 'Print Design',
            'title': p.title,
            'meta': 'Print Design',
            'tech': [],
            'link': '',
            'image': '/media/%s' % p.image if p.image else None,
            'kind': 'print',
        })

    for i, p in enumerate(post_design[:GRAPHICS_POST_LIMIT]):
        items.append({
            'group': 'design',
            'group_label': 'Social Media',
            'title': p.title,
            'meta': 'Social Media Post',
            'tech': [],
            'link': '',
            'image': '/media/%s' % p.image if p.image else None,
            'kind': 'post',
        })

    # Attach a rotating placeholder filename so cards without an image still
    # render something recognisable until real artwork is uploaded.
    for i, item in enumerate(items):
        item['placeholder'] = 'project-%d.svg' % ((i % PLACEHOLDER_TONES) + 1)

    return items


def build_client_logos(clients):
    """Shape Client_Logo rows for the homepage marquee.

    Returns a list of dicts, falling back to the bundled placeholder marks
    when nothing has been uploaded yet so the section is never empty:
      title -> company name
      url   -> media URL or a placeholder path
      href  -> external site, or '' when the row has no link
    """
    items = [
        {
            'title': c.title,
            'url': '/media/%s' % c.image if c.image else '',
            'href': c.target_url,
        }
        for c in clients
        if c.image
    ]

    if items:
        return items

    return [
        {
            'title': '',
            'url': '/static/images/placeholders/client-%d.svg' % n,
            'href': '',
        }
        for n in range(1, PLACEHOLDER_TONES + 1)
    ]


def build_graphics_photos(print_design, post_design):
    """Shape the graphics models for the bare photo grid.

    Deliberately carries no meta/tech/badge data — the tiles must show nothing
    but the photo. The title is only ever read by the lightbox, which is why it
    is kept here rather than dropped:
      title -> lightbox caption
      url   -> full-size media URL, and the href the lightbox opens
      kind  -> print | post, kept for grouping/debugging only
    """
    photos = [
        {'title': p.title, 'url': '/media/%s' % p.image, 'kind': 'print'}
        for p in print_design if p.image
    ]
    photos += [
        {'title': p.title, 'url': '/media/%s' % p.image, 'kind': 'post'}
        for p in post_design if p.image
    ]
    return photos


def portfolio_group_counts(items):
    """Count items per filter bucket (always includes every key)."""
    keys = ['website', 'software', 'ecommerce', 'design', 'video']
    counts = {k: 0 for k in keys}
    for item in items:
        if item['group'] in counts:
            counts[item['group']] += 1
    return counts


# Portfolio Page
def portfolio(request):
    blog_posts = Blog_Post.objects.all()[:3][::-1]
    website_portfolio = Website_Portfolio.objects.all()
    print_design = Print_Design.objects.all()
    post_design = Post_Design.objects.all().order_by('-id')
    testimonial = Testimonial.objects.all()
    client_logos = build_client_logos(Client_Logo.objects.all())
    pricing_plans = Pricing_Plan.objects.filter(is_active=True)

    portfolio_items = build_portfolio_items(website_portfolio, print_design, post_design)

    return render(request, 'portfolio/portfolio.html', {
        "blog_posts": blog_posts,
        "website_portfolio": website_portfolio,
        "print_design": print_design,
        "post_design": post_design,
        "testimonial": testimonial,
        "client_logos": client_logos,
        "pricing_plans": pricing_plans,
        "portfolio_items": portfolio_items,
        "portfolio_total": len(portfolio_items),
        "group_counts": portfolio_group_counts(portfolio_items),
    })


def all_work(request):
    """Web, software and e-commerce work — every item, no paging.

    Graphics lives on its own page (see graphics_portfolio) because it is
    presented completely differently: bare photos instead of titled cards.
    """
    website_portfolio = Website_Portfolio.objects.all()
    print_design = Print_Design.objects.all()
    post_design = Post_Design.objects.all().order_by('-id')

    all_items = build_portfolio_items(website_portfolio, print_design, post_design)
    cards = [i for i in all_items if i['group'] != 'design']

    return render(request, 'portfolio/all_work.html', {
        'cards': cards,
        'card_total': len(cards),
        'photo_total': Print_Design.objects.count() + Post_Design.objects.count(),
        'counts': portfolio_group_counts(all_items),
    })


def graphics_portfolio(request):
    """Every graphics piece — print designs and social media posts.

    No filters and no text on the tiles: the grid is photos only, and the
    lightbox caption is the single place a title appears.
    """
    photos = build_graphics_photos(
        Print_Design.objects.all(),
        Post_Design.objects.all().order_by('-id'),
    )

    return render(request, 'portfolio/graphics_portfolio.html', {
        'photos': photos,
        'photo_total': len(photos),
    })


def about_us(request):
    testimonial = Testimonial.objects.all()
    return render(request, 'portfolio/about.html', {'testimonial': testimonial})


def contact_us(request):
    if request.method == "POST":
        mail = request.POST.get('mail')
        subject = request.POST.get('subject')
        message = request.POST.get('message')
        contact = Contact(mail=mail, subject=subject, message=message)
        contact.save()
        messages.success(request, 'Message Sent Succesfully')
        return redirect('portfolio')
    else:
        return render(request, 'portfolio/contact.html', {})
