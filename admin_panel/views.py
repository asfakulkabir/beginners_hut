"""Views for the custom admin panel mounted at /admin/.

Notes on the shape of this module, because it replaced a version where every
view was a bare ``if request.user.is_superuser`` chain:

* ``staff_required`` is the single entry gate. It guarantees an authenticated
  superuser and, when a plain user hits it, hands back a 403 instead of the
  old behaviour of falling through and returning ``None`` (a 500).
* Deletes are POST-only. They used to be ``<a href>`` GET links, which meant a
  prefetch or a crawler could wipe content.
* Every list is paginated and searchable; the inbox had 524 rows rendered as
  1048 Flowbite modals.
* ``next`` params survive redirects so a delete lands you back on the page you
  were looking at.
"""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.db.models.functions import TruncMonth
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST

from blog.models import Blog_Post
from portfolio.models import (
    Client_Logo,
    Contact,
    Post_Design,
    Pricing_Plan,
    Print_Design,
    Testimonial,
    Website_Portfolio,
)

from .forms import (
    BlogPostForm,
    ClientLogoForm,
    PostDesignForm,
    PricingPlanForm,
    PrintDesignForm,
    TestimonialForm,
    WebsitePortfolioForm,
)

PER_PAGE = 15


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------
def staff_required(view_func):
    """Only superusers reach the panel.

    ``login_required`` does the redirect for anonymous visitors; anything
    logged in but not a superuser gets a 403 rather than a silent failure.
    """

    @login_required(login_url=reverse_lazy('admin_panel:admin_login'))
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_superuser:
            messages.error(request, 'That account does not have admin access.')
            return redirect('admin_panel:admin_login')
        return view_func(request, *args, **kwargs)

    _wrapped.__name__ = view_func.__name__
    _wrapped.__doc__ = view_func.__doc__
    return _wrapped


def paginate(request, queryset, per_page=PER_PAGE):
    paginator = Paginator(queryset, per_page)
    page = paginator.get_page(request.GET.get('page'))

    # Page-number window for the pager: first, last, and two either side of the
    # current page, with gaps collapsed into an ellipsis. Done here because the
    # template would otherwise need nested loop arithmetic.
    numbers = list(paginator.page_range)
    if len(numbers) <= 7:
        page.window = numbers
    else:
        window = [numbers[0]]
        start = max(2, page.number - 1)
        end = min(paginator.num_pages - 1, page.number + 1)
        if start > 2:
            window.append('…')
        window.extend(range(start, end + 1))
        if end < paginator.num_pages - 1:
            window.append('…')
        window.append(numbers[-1])
        page.window = window

    return page


def search(queryset, request, fields):
    """Filter ``queryset`` by the ``q`` GET param across ``fields``.

    Falls back to ``objects.all()`` when the field list is empty so callers
    never have to branch.
    """
    term = (request.GET.get('q') or '').strip()
    if not term or not fields:
        return queryset, term
    query = Q()
    for field in fields:
        query |= Q(**{f'{field}__icontains': term})
    return queryset.filter(query), term


def safe_next(request, default):
    """Return a same-site redirect target from ``?next=``.

    Checks POST first because delete buttons post a hidden ``next`` field, then
    GET. Anything that is not a local path is ignored, so ``?next=//evil.test``
    or ``?next=https://evil.test`` cannot be used to bounce an admin off-site
    after a write.
    """
    candidate = (request.POST.get('next') or request.GET.get('next') or '').strip()
    if candidate.startswith('/') and not candidate.startswith('//'):
        return candidate
    return default


def apply_clear_image(form, obj):
    """Honour the ``clear_image`` switch, or keep a freshly uploaded file.

    The old file is left on disk rather than deleted: the same upload may be
    referenced by a blog post's content, and an unlink in one screen should
    not 404 the rest of the site.
    """
    if not obj.image:
        return
    if form.cleaned_data.get('clear_image'):
        obj.image = None
    elif form.cleaned_data.get('image'):
        obj.image = form.cleaned_data['image']


def form_page(form, heading, sub, back_url, submit_label, **extra):
    """Shared context for every add/edit screen."""
    return {
        'form': form,
        'heading': heading,
        'sub': sub,
        'back_url': back_url,
        'submit_label': submit_label,
        **extra,
    }


def month_label(value):
    """'Mar' for a TruncMonth bucket, in the project's timezone."""
    return (timezone.localtime(value) if timezone.is_aware(value) else value).strftime('%b')


# --------------------------------------------------------------------------
# auth
# --------------------------------------------------------------------------
def admin_login(request):
    if request.user.is_authenticated:
        if request.user.is_superuser:
            return redirect('admin_panel:dashboard')
        # Logged in but not allowed in: drop the session and show the form here
        # rather than redirecting to a page that would redirect again.
        messages.error(request, 'That account does not have admin access.')
        logout(request)
        return render(request, 'login.html')

    if request.method == 'POST':
        user_obj = authenticate(
            request,
            username=(request.POST.get('username') or '').strip(),
            password=request.POST.get('password') or '',
        )
        if user_obj and user_obj.is_superuser:
            login(request, user_obj)
            messages.success(request, f'Welcome back, {user_obj.get_short_name() or user_obj.username}.')
            return redirect(safe_next(request, reverse('admin_panel:dashboard')))
        if user_obj:
            messages.error(request, 'That account does not have admin access.')
        else:
            messages.error(request, 'Wrong username or password.')
        return render(request, 'login.html', {'username': request.POST.get('username', '')})

    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out.')
    return redirect('admin_panel:admin_login')


# --------------------------------------------------------------------------
# dashboard
# --------------------------------------------------------------------------
@staff_required
def dashboard(request):
    now = timezone.now()
    month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    totals = {
        'contacts': Contact.objects.count(),
        'contacts_unread': Contact.objects.filter(is_read=False).count(),
        'contacts_month': Contact.objects.filter(time__gte=month_start).count(),
        'posts': Blog_Post.objects.count(),
        'posts_published': Blog_Post.objects.filter(is_published=True).count(),
        'posts_draft': Blog_Post.objects.filter(is_published=False).count(),
        'posts_month': Blog_Post.objects.filter(date_time__gte=month_start).count(),
        'views': sum(Blog_Post.objects.values_list('view_count', flat=True)),
        'websites': Website_Portfolio.objects.count(),
        'print_designs': Print_Design.objects.count(),
        'post_designs': Post_Design.objects.count(),
        'testimonials': Testimonial.objects.count(),
        'client_logos': Client_Logo.objects.count(),
        'pricing_plans': Pricing_Plan.objects.count(),
    }

    # 6-month message volume, oldest first so the chart reads left to right.
    months = (
        Contact.objects.filter(time__gte=month_start - timedelta(days=182))
        .annotate(month=TruncMonth('time'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )
    chart = {
        'labels': [month_label(m['month']) for m in months],
        'data': [m['total'] for m in months],
    }

    return render(
        request,
        'dashboard/dashboard.html',
        {
            'totals': totals,
            'chart': chart,
            'recent_contacts': Contact.objects.all()[:6],
            'recent_posts': Blog_Post.objects.all()[:5],
            'now': now,
        },
    )


# --------------------------------------------------------------------------
# contact inbox
# --------------------------------------------------------------------------
@staff_required
def contact_message(request):
    queryset, term = search(Contact.objects.all(), request, ['mail', 'subject', 'message'])

    state = (request.GET.get('state') or 'all').strip()
    if state == 'unread':
        queryset = queryset.filter(is_read=False)
    elif state == 'read':
        queryset = queryset.filter(is_read=True)

    return render(
        request,
        'dashboard/contact_message.html',
        {
            'contacts': paginate(request, queryset),
            'term': term,
            'state': state,
            'unread_total': Contact.objects.filter(is_read=False).count(),
            'read_total': Contact.objects.filter(is_read=True).count(),
            'total': Contact.objects.count(),
        },
    )


@staff_required
@require_POST
def toggle_contact_read(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    was_read = contact.is_read
    contact.mark_unread() if was_read else contact.mark_read()
    messages.success(request, 'Message marked as unread.' if was_read else 'Message marked as read.')
    return redirect(safe_next(request, reverse('admin_panel:contact_message')))


@staff_required
@require_POST
def delete_contact(request, pk):
    contact = get_object_or_404(Contact, pk=pk)
    who = contact.mail
    contact.delete()
    messages.success(request, f'Message from {who} deleted.')
    return redirect(safe_next(request, reverse('admin_panel:contact_message')))


# --------------------------------------------------------------------------
# blog
# --------------------------------------------------------------------------
@staff_required
def blog(request):
    queryset, term = search(Blog_Post.objects.all(), request, ['title', 'category', 'author', 'content'])

    state = (request.GET.get('state') or 'all').strip()
    if state == 'published':
        queryset = queryset.filter(is_published=True)
    elif state == 'draft':
        queryset = queryset.filter(is_published=False)

    return render(
        request,
        'dashboard/blog.html',
        {
            'blog_posts': paginate(request, queryset),
            'term': term,
            'state': state,
            'published_total': Blog_Post.objects.filter(is_published=True).count(),
            'draft_total': Blog_Post.objects.filter(is_published=False).count(),
            'total': Blog_Post.objects.count(),
        },
    )


@staff_required
def add_blog(request):
    form = BlogPostForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        post = form.save()
        messages.success(
            request,
            f'“{post.title}” published.' if post.is_published else f'“{post.title}” saved as a draft.',
        )
        return redirect(reverse('admin_panel:blog'))

    return render(
        request,
        'dashboard/blog_form.html',
        form_page(
            form,
            'New blog post',
            'Write it once, publish when it is ready.',
            reverse('admin_panel:blog'),
            'Save post',
        ),
    )


@staff_required
def update_blog(request, pk):
    post = get_object_or_404(Blog_Post, pk=pk)
    form = BlogPostForm(request.POST or None, request.FILES or None, instance=post)
    if request.method == 'POST' and form.is_valid():
        apply_clear_image(form, post)
        form.save()
        messages.success(request, f'“{post.title}” updated.')
        return redirect(reverse('admin_panel:blog'))

    return render(
        request,
        'dashboard/blog_form.html',
        form_page(
            form,
            'Edit post',
            post.title,
            reverse('admin_panel:blog'),
            'Save changes',
        ),
    )


@staff_required
@require_POST
def delete_blog(request, pk):
    post = get_object_or_404(Blog_Post, pk=pk)
    title = post.title
    post.delete()
    messages.success(request, f'“{title}” deleted.')
    return redirect(safe_next(request, reverse('admin_panel:blog')))


@staff_required
@require_POST
def toggle_blog_published(request, pk):
    post = get_object_or_404(Blog_Post, pk=pk)
    post.is_published = not post.is_published
    post.save(update_fields=['is_published'])
    messages.success(
        request,
        f'“{post.title}” is now {"live" if post.is_published else "a draft"}.',
    )
    return redirect(safe_next(request, reverse('admin_panel:blog')))


# --------------------------------------------------------------------------
# portfolio: one hub page, three collections
# --------------------------------------------------------------------------
@staff_required
def portfolio_admin(request):
    def section(model, term_fields):
        queryset, term = search(model.objects.order_by('-id'), request, term_fields)
        return paginate(request, queryset, per_page=10), term

    websites, website_term = section(Website_Portfolio, ['title', 'category', 'technology'])
    prints, print_term = section(Print_Design, ['title'])
    posts, post_term = section(Post_Design, ['title'])

    return render(
        request,
        'dashboard/portfolio_admin.html',
        {
            'website_portfolio': websites,
            'print_design': prints,
            'post_design': posts,
            'website_term': website_term,
            'print_term': print_term,
            'post_term': post_term,
            'tab': (request.GET.get('tab') or 'website'),
            'counts': {
                'website': Website_Portfolio.objects.count(),
                'print': Print_Design.objects.count(),
                'post': Post_Design.objects.count(),
            },
        },
    )


@staff_required
def add_print_design(request):
    form = PrintDesignForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        design = form.save()
        messages.success(request, f'“{design.title}” added to print designs.')
        return redirect(f'{reverse("admin_panel:portfolio_admin")}?tab=print')

    return render(
        request,
        'dashboard/image_form.html',
        form_page(
            form,
            'New print design',
            'Recommended 3000 x 1110 px so it fills the print strip without letterboxing.',
            f'{reverse("admin_panel:portfolio_admin")}?tab=print',
            'Add design',
        ),
    )


@staff_required
def update_print_design(request, pk):
    design = get_object_or_404(Print_Design, pk=pk)
    form = PrintDesignForm(request.POST or None, request.FILES or None, instance=design)
    if request.method == 'POST' and form.is_valid():
        apply_clear_image(form, design)
        form.save()
        messages.success(request, f'“{design.title}” updated.')
        return redirect(f'{reverse("admin_panel:portfolio_admin")}?tab=print')

    return render(
        request,
        'dashboard/image_form.html',
        form_page(
            form,
            'Edit print design',
            design.title,
            f'{reverse("admin_panel:portfolio_admin")}?tab=print',
            'Save changes',
        ),
    )


@staff_required
@require_POST
def delete_print_design(request, pk):
    design = get_object_or_404(Print_Design, pk=pk)
    title = design.title
    design.delete()
    messages.success(request, f'Print design “{title}” deleted.')
    return redirect(safe_next(request, f'{reverse("admin_panel:portfolio_admin")}?tab=print'))


@staff_required
def add_post_design(request):
    form = PostDesignForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        design = form.save()
        messages.success(request, f'“{design.title}” added to post designs.')
        return redirect(f'{reverse("admin_panel:portfolio_admin")}?tab=post')

    return render(
        request,
        'dashboard/image_form.html',
        form_page(
            form,
            'New post design',
            'Recommended 3000 x 1110 px so it fills the social strip without letterboxing.',
            f'{reverse("admin_panel:portfolio_admin")}?tab=post',
            'Add design',
        ),
    )


@staff_required
def update_post_design(request, pk):
    design = get_object_or_404(Post_Design, pk=pk)
    form = PostDesignForm(request.POST or None, request.FILES or None, instance=design)
    if request.method == 'POST' and form.is_valid():
        apply_clear_image(form, design)
        form.save()
        messages.success(request, f'“{design.title}” updated.')
        return redirect(f'{reverse("admin_panel:portfolio_admin")}?tab=post')

    return render(
        request,
        'dashboard/image_form.html',
        form_page(
            form,
            'Edit post design',
            design.title,
            f'{reverse("admin_panel:portfolio_admin")}?tab=post',
            'Save changes',
        ),
    )


@staff_required
@require_POST
def delete_post_design(request, pk):
    design = get_object_or_404(Post_Design, pk=pk)
    title = design.title
    design.delete()
    messages.success(request, f'Post design “{title}” deleted.')
    return redirect(safe_next(request, f'{reverse("admin_panel:portfolio_admin")}?tab=post'))


@staff_required
def add_website_portfolio(request):
    form = WebsitePortfolioForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        site = form.save()
        messages.success(request, f'“{site.title}” added to the website portfolio.')
        return redirect(f'{reverse("admin_panel:portfolio_admin")}?tab=website')

    return render(
        request,
        'dashboard/website_form.html',
        form_page(
            form,
            'New website project',
            'Everything here feeds the public portfolio filters.',
            f'{reverse("admin_panel:portfolio_admin")}?tab=website',
            'Add project',
        ),
    )


@staff_required
def update_website_portfolio(request, pk):
    site = get_object_or_404(Website_Portfolio, pk=pk)
    form = WebsitePortfolioForm(request.POST or None, request.FILES or None, instance=site)
    if request.method == 'POST' and form.is_valid():
        apply_clear_image(form, site)
        form.save()
        messages.success(request, f'“{site.title}” updated.')
        return redirect(f'{reverse("admin_panel:portfolio_admin")}?tab=website')

    return render(
        request,
        'dashboard/website_form.html',
        form_page(
            form,
            'Edit website project',
            site.title,
            f'{reverse("admin_panel:portfolio_admin")}?tab=website',
            'Save changes',
        ),
    )


@staff_required
@require_POST
def delete_website_portfolio(request, pk):
    site = get_object_or_404(Website_Portfolio, pk=pk)
    title = site.title
    site.delete()
    messages.success(request, f'Website project “{title}” deleted.')
    return redirect(safe_next(request, f'{reverse("admin_panel:portfolio_admin")}?tab=website'))


# --------------------------------------------------------------------------
# testimonials
# --------------------------------------------------------------------------
@staff_required
def testimonial(request):
    queryset, term = search(Testimonial.objects.order_by('-id'), request, ['title', 'content'])
    return render(
        request,
        'dashboard/testimonial.html',
        {
            'testimonial': paginate(request, queryset),
            'term': term,
            'total': Testimonial.objects.count(),
        },
    )


@staff_required
def add_testimonial(request):
    form = TestimonialForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        item = form.save()
        messages.success(request, f'Testimonial from {item.title} added.')
        return redirect(reverse('admin_panel:testimonial'))

    return render(
        request,
        'dashboard/image_form.html',
        form_page(
            form,
            'New testimonial',
            'Shown as a quote card on the homepage.',
            reverse('admin_panel:testimonial'),
            'Add testimonial',
        ),
    )


@staff_required
def update_testimonial(request, pk):
    item = get_object_or_404(Testimonial, pk=pk)
    form = TestimonialForm(request.POST or None, request.FILES or None, instance=item)
    if request.method == 'POST' and form.is_valid():
        apply_clear_image(form, item)
        form.save()
        messages.success(request, f'Testimonial from {item.title} updated.')
        return redirect(reverse('admin_panel:testimonial'))

    return render(
        request,
        'dashboard/image_form.html',
        form_page(
            form,
            'Edit testimonial',
            item.title,
            reverse('admin_panel:testimonial'),
            'Save changes',
        ),
    )


@staff_required
@require_POST
def delete_testimonial(request, pk):
    item = get_object_or_404(Testimonial, pk=pk)
    title = item.title
    item.delete()
    messages.success(request, f'Testimonial from {title} deleted.')
    return redirect(safe_next(request, reverse('admin_panel:testimonial')))


# --------------------------------------------------------------------------
# client logos
# --------------------------------------------------------------------------
@staff_required
def client_logo(request):
    queryset, term = search(Client_Logo.objects.order_by('id'), request, ['title', 'link'])
    return render(
        request,
        'dashboard/client_logo.html',
        {
            'logos': paginate(request, queryset),
            'term': term,
            'total': Client_Logo.objects.count(),
        },
    )


@staff_required
def add_client_logo(request):
    form = ClientLogoForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        logo = form.save()
        messages.success(request, f'“{logo.title}” added to the homepage marquee.')
        return redirect(reverse('admin_panel:client_logo'))

    return render(
        request,
        'dashboard/client_logo_form.html',
        form_page(
            form,
            'New client logo',
            'Logos render in a fixed 160 x 44 box, so any shape lines up with the rest.',
            reverse('admin_panel:client_logo'),
            'Add logo',
            marquee=Client_Logo.objects.all()[:12],
        ),
    )


@staff_required
def update_client_logo(request, pk):
    logo = get_object_or_404(Client_Logo, pk=pk)
    form = ClientLogoForm(request.POST or None, request.FILES or None, instance=logo)
    if request.method == 'POST' and form.is_valid():
        apply_clear_image(form, logo)
        form.save()
        messages.success(request, f'“{logo.title}” updated.')
        return redirect(reverse('admin_panel:client_logo'))

    return render(
        request,
        'dashboard/client_logo_form.html',
        form_page(
            form,
            'Edit client logo',
            logo.title,
            reverse('admin_panel:client_logo'),
            'Save changes',
            marquee=Client_Logo.objects.all()[:12],
        ),
    )


@staff_required
@require_POST
def delete_client_logo(request, pk):
    logo = get_object_or_404(Client_Logo, pk=pk)
    title = logo.title
    logo.delete()
    messages.success(request, f'Logo “{title}” removed from the marquee.')
    return redirect(safe_next(request, reverse('admin_panel:client_logo')))


# --------------------------------------------------------------------------
# pricing
# --------------------------------------------------------------------------
@staff_required
def pricing(request):
    queryset, term = search(
        Pricing_Plan.objects.all(), request, ['title', 'tagline', 'price', 'description']
    )
    return render(
        request,
        'dashboard/pricing.html',
        {
            'plans': paginate(request, queryset),
            'term': term,
            'total': Pricing_Plan.objects.count(),
            'active_total': Pricing_Plan.objects.filter(is_active=True).count(),
        },
    )


@staff_required
def add_pricing(request):
    form = PricingPlanForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        plan = form.save()
        messages.success(request, f'“{plan.title}” added to the pricing section.')
        return redirect(reverse('admin_panel:pricing'))

    return render(
        request,
        'dashboard/pricing_form.html',
        form_page(
            form,
            'New pricing plan',
            'Shown as a card in the homepage pricing section.',
            reverse('admin_panel:pricing'),
            'Add plan',
        ),
    )


@staff_required
def update_pricing(request, pk):
    plan = get_object_or_404(Pricing_Plan, pk=pk)
    form = PricingPlanForm(request.POST or None, instance=plan)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'“{plan.title}” updated.')
        return redirect(reverse('admin_panel:pricing'))

    return render(
        request,
        'dashboard/pricing_form.html',
        form_page(
            form,
            'Edit pricing plan',
            plan.title,
            reverse('admin_panel:pricing'),
            'Save changes',
        ),
    )


@staff_required
@require_POST
def toggle_pricing_active(request, pk):
    plan = get_object_or_404(Pricing_Plan, pk=pk)
    plan.is_active = not plan.is_active
    plan.save(update_fields=['is_active'])
    messages.success(
        request,
        f'“{plan.title}” is now {"visible" if plan.is_active else "hidden"}.',
    )
    return redirect(safe_next(request, reverse('admin_panel:pricing')))


@staff_required
@require_POST
def delete_pricing(request, pk):
    plan = get_object_or_404(Pricing_Plan, pk=pk)
    title = plan.title
    plan.delete()
    messages.success(request, f'Pricing plan “{title}” deleted.')
    return redirect(safe_next(request, reverse('admin_panel:pricing')))
