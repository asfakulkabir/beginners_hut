"""Tests for the custom admin panel.

These cover the behaviour the previous panel got wrong rather than pixel-level
markup: who can reach the panel, that deletes cannot happen over GET, that
validation is real, and that pagination/search keep the inbox usable.
"""

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

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


def png_bytes():
    """Smallest valid 1x1 PNG, so ImageField validation passes."""
    return (
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06'
        b'\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05'
        b'\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )


class AdminAuthTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'pw12345')
        self.staff = User.objects.create_user('staffy', 'staff@example.com', 'pw12345')

    def test_anonymous_is_sent_to_the_login_page(self):
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].startswith(reverse('admin_panel:admin_login')))

    def test_non_superuser_cannot_reach_the_panel(self):
        self.client.force_login(self.staff)
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertRedirects(response, reverse('admin_panel:admin_login'))

    def test_login_rejects_a_non_superuser(self):
        response = self.client.post(
            reverse('admin_panel:admin_login'),
            {'username': 'staffy', 'password': 'pw12345'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'does not have admin access')
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_login_rejects_a_wrong_password_without_500(self):
        response = self.client.post(
            reverse('admin_panel:admin_login'),
            {'username': 'boss', 'password': 'nope'},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Wrong username or password')

    def test_login_sends_a_superuser_to_the_dashboard(self):
        response = self.client.post(
            reverse('admin_panel:admin_login'),
            {'username': 'boss', 'password': 'pw12345'},
        )
        self.assertRedirects(response, reverse('admin_panel:dashboard'))

    def test_login_ignores_an_offsite_next(self):
        response = self.client.post(
            reverse('admin_panel:admin_login') + '?next=https://evil.test/steal',
            {'username': 'boss', 'password': 'pw12345'},
        )
        self.assertRedirects(response, reverse('admin_panel:dashboard'))

    def test_every_list_screen_renders(self):
        self.client.force_login(self.admin)
        for name in ['dashboard', 'contact_message', 'blog', 'portfolio_admin', 'testimonial', 'client_logo', 'pricing']:
            with self.subTest(screen=name):
                self.assertEqual(self.client.get(reverse(f'admin_panel:{name}')).status_code, 200)

    def test_every_add_screen_renders(self):
        self.client.force_login(self.admin)
        for name in [
            'add_blog',
            'add_website_portfolio',
            'add_print_design',
            'add_post_design',
            'add_testimonial',
            'add_client_logo',
            'add_pricing',
        ]:
            with self.subTest(screen=name):
                self.assertEqual(self.client.get(reverse(f'admin_panel:{name}')).status_code, 200)


class DashboardTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'pw')
        self.client.force_login(self.admin)
        Contact.objects.create(mail='a@example.com', subject='Hello', message='First')
        Contact.objects.create(mail='b@example.com', subject='Second', message='Second')
        Blog_Post.objects.create(
            title='Post one', category='Design', author='Asfakul', content='<p>Body</p>'
        )

    def test_dashboard_shows_counts(self):
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertContains(response, 'Messages')
        self.assertContains(response, 'Blog posts')
        self.assertContains(response, 'a@example.com')
        self.assertContains(response, 'Post one')

    def test_dashboard_unread_badge_counts_only_new_mail(self):
        unread = Contact.objects.get(subject='Hello')
        self.assertEqual(unread.is_read, False)

        Contact.objects.get(subject='Second').mark_read()
        response = self.client.get(reverse('admin_panel:dashboard'))
        self.assertEqual(response.context['totals']['contacts_unread'], 1)
        self.assertEqual(response.context['totals']['contacts'], 2)


class BlogCrudTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'pw')
        self.client.force_login(self.admin)

    def test_create_a_post(self):
        response = self.client.post(
            reverse('admin_panel:add_blog'),
            {
                'title': 'A brand new post',
                'category': 'Web Design',
                'author': 'Asfakul',
                'about_author': '',
                'author_profile_link': '',
                'content': '<p>Hello world</p>',
                'meta_description': 'Short summary.',
                'is_published': 'on',
            },
        )
        self.assertRedirects(response, reverse('admin_panel:blog'))
        post = Blog_Post.objects.get()
        self.assertEqual(post.title, 'A brand new post')
        self.assertTrue(post.is_published)
        self.assertEqual(post.slug, 'a-brand-new-post')

    def test_a_post_without_a_title_is_rejected(self):
        self.client.post(
            reverse('admin_panel:add_blog'),
            {'title': '', 'category': 'x', 'author': 'y', 'content': 'z'},
        )
        self.assertEqual(Blog_Post.objects.count(), 0)

    def test_an_overlong_meta_description_is_rejected(self):
        self.client.post(
            reverse('admin_panel:add_blog'),
            {
                'title': 'Fine title',
                'category': 'x',
                'author': 'y',
                'content': 'z',
                'meta_description': 'x' * 200,
            },
        )
        self.assertEqual(Blog_Post.objects.count(), 0)

    def test_edit_a_post(self):
        post = Blog_Post.objects.create(title='Before', category='x', author='y')
        self.client.post(
            reverse('admin_panel:update_blog', args=[post.pk]),
            {
                'title': 'After',
                'category': 'x',
                'author': 'y',
                'content': '<p>z</p>',
                'is_published': 'on',
            },
        )
        post.refresh_from_db()
        self.assertEqual(post.title, 'After')

    def test_edit_keeps_the_existing_image_when_none_is_uploaded(self):
        post = Blog_Post.objects.create(title='Has art', category='x', author='y')
        post.image.save('keep.png', SimpleUploadedFile('keep.png', png_bytes()), save=True)
        name = post.image.name

        self.client.post(
            reverse('admin_panel:update_blog', args=[post.pk]),
            {'title': 'Renamed', 'category': 'x', 'author': 'y', 'content': 'z'},
        )
        post.refresh_from_db()
        self.assertEqual(post.image.name, name)

    def test_clear_image_removes_the_file_reference(self):
        post = Blog_Post.objects.create(title='Has art', category='x', author='y')
        post.image.save('drop.png', SimpleUploadedFile('drop.png', png_bytes()), save=True)

        self.client.post(
            reverse('admin_panel:update_blog', args=[post.pk]),
            {
                'title': 'No art',
                'category': 'x',
                'author': 'y',
                'content': 'z',
                'clear_image': 'on',
            },
        )
        post.refresh_from_db()
        self.assertFalse(post.image)

    def test_toggle_published(self):
        post = Blog_Post.objects.create(title='Draft me', category='x', author='y')
        self.assertTrue(post.is_published)

        self.client.post(reverse('admin_panel:toggle_blog_published', args=[post.pk]))
        post.refresh_from_db()
        self.assertFalse(post.is_published)

        self.client.post(reverse('admin_panel:toggle_blog_published', args=[post.pk]))
        post.refresh_from_db()
        self.assertTrue(post.is_published)

    def test_delete_over_get_is_refused(self):
        post = Blog_Post.objects.create(title='Keep me', category='x', author='y')
        response = self.client.get(reverse('admin_panel:delete_blog', args=[post.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Blog_Post.objects.filter(pk=post.pk).exists())

    def test_delete_over_post(self):
        post = Blog_Post.objects.create(title='Drop me', category='x', author='y')
        self.client.post(reverse('admin_panel:delete_blog', args=[post.pk]))
        self.assertFalse(Blog_Post.objects.filter(pk=post.pk).exists())

    def test_delete_returns_to_the_page_you_were_on(self):
        post = Blog_Post.objects.create(title='Drop me', category='x', author='y')
        response = self.client.post(
            reverse('admin_panel:delete_blog', args=[post.pk]),
            {'next': '/admin/blog/?state=draft'},
        )
        self.assertRedirects(response, '/admin/blog/?state=draft')

    def test_search_and_state_filters(self):
        Blog_Post.objects.create(title='Django tips', category='code', author='a')
        Blog_Post.objects.create(title='Logo work', category='design', author='a')
        Blog_Post.objects.create(title='Hidden draft', category='code', author='a', is_published=False)

        response = self.client.get(reverse('admin_panel:blog'), {'q': 'django'})
        self.assertEqual(len(response.context['blog_posts']), 1)
        self.assertContains(response, 'Django tips')

        response = self.client.get(reverse('admin_panel:blog'), {'state': 'draft'})
        self.assertEqual(len(response.context['blog_posts']), 1)
        self.assertContains(response, 'Hidden draft')

    def test_pagination_splits_a_long_list(self):
        for i in range(20):
            Blog_Post.objects.create(title=f'Post {i:02d}', category='x', author='a')

        response = self.client.get(reverse('admin_panel:blog'))
        self.assertEqual(len(response.context['blog_posts']), 15)

        response = self.client.get(reverse('admin_panel:blog'), {'page': 2})
        self.assertEqual(len(response.context['blog_posts']), 5)
        self.assertEqual(response.context['blog_posts'].window[-1], 2)


class ContactInboxTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'pw')
        self.client.force_login(self.admin)
        self.first = Contact.objects.create(mail='one@example.com', subject='First', message='Body one')
        self.second = Contact.objects.create(mail='two@example.com', subject='Second', message='Body two')

    def test_inbox_paginates(self):
        for i in range(40):
            Contact.objects.create(mail=f'bulk{i}@example.com', subject=f'Bulk {i}', message='x')
        response = self.client.get(reverse('admin_panel:contact_message'))
        self.assertEqual(len(response.context['contacts']), 15)

    def test_search_matches_subject_mail_and_body(self):
        response = self.client.get(reverse('admin_panel:contact_message'), {'q': 'Body two'})
        self.assertEqual([c.pk for c in response.context['contacts']], [self.second.pk])

    def test_mark_read_and_unread(self):
        self.client.post(reverse('admin_panel:toggle_contact_read', args=[self.first.pk]))
        self.first.refresh_from_db()
        self.assertTrue(self.first.is_read)
        self.assertIsNotNone(self.first.read_at)

        self.client.post(reverse('admin_panel:toggle_contact_read', args=[self.first.pk]))
        self.first.refresh_from_db()
        self.assertFalse(self.first.is_read)
        self.assertIsNone(self.first.read_at)

    def test_unread_filter(self):
        self.second.mark_read()
        response = self.client.get(reverse('admin_panel:contact_message'), {'state': 'unread'})
        self.assertEqual([c.pk for c in response.context['contacts']], [self.first.pk])

    def test_delete_over_get_is_refused(self):
        response = self.client.get(reverse('admin_panel:delete_contact', args=[self.first.pk]))
        self.assertEqual(response.status_code, 405)
        self.assertTrue(Contact.objects.filter(pk=self.first.pk).exists())

    def test_delete_over_post(self):
        self.client.post(reverse('admin_panel:delete_contact', args=[self.first.pk]))
        self.assertFalse(Contact.objects.filter(pk=self.first.pk).exists())


class PortfolioCrudTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'pw')
        self.client.force_login(self.admin)

    def test_website_round_trip(self):
        response = self.client.post(
            reverse('admin_panel:add_website_portfolio'),
            {
                'title': 'Aurora Shop',
                'category': 'E-Commerce',
                'technology': 'Django, Tailwind',
                'link': 'https://aurora.test',
            },
        )
        self.assertEqual(response.status_code, 302)
        site = Website_Portfolio.objects.get()
        self.assertEqual(site.group, 'ecommerce')

        self.client.post(
            reverse('admin_panel:update_website_portfolio', args=[site.pk]),
            {
                'title': 'Aurora Store',
                'category': 'E-Commerce',
                'technology': 'Django',
                'link': 'https://aurora.test',
            },
        )
        site.refresh_from_db()
        self.assertEqual(site.title, 'Aurora Store')

        self.client.post(reverse('admin_panel:delete_website_portfolio', args=[site.pk]))
        self.assertEqual(Website_Portfolio.objects.count(), 0)

    def test_website_requires_a_valid_link(self):
        self.client.post(
            reverse('admin_panel:add_website_portfolio'),
            {'title': 'Bad', 'category': 'x', 'technology': 'y', 'link': 'not a url'},
        )
        self.assertEqual(Website_Portfolio.objects.count(), 0)

    def test_print_and_post_design_round_trip(self):
        for add, edit, delete, model in [
            ('add_print_design', 'update_print_design', 'delete_print_design', Print_Design),
            ('add_post_design', 'update_post_design', 'delete_post_design', Post_Design),
        ]:
            with self.subTest(model=model.__name__):
                self.client.post(reverse(f'admin_panel:{add}'), {'title': 'Design one'})
                obj = model.objects.get()
                self.assertEqual(obj.title, 'Design one')

                self.client.post(reverse(f'admin_panel:{edit}', args=[obj.pk]), {'title': 'Design two'})
                obj.refresh_from_db()
                self.assertEqual(obj.title, 'Design two')

                self.client.post(reverse(f'admin_panel:{delete}', args=[obj.pk]))
                self.assertEqual(model.objects.count(), 0)

    def test_testimonial_round_trip_and_length_check(self):
        self.client.post(
            reverse('admin_panel:add_testimonial'),
            {'title': 'Sarah Islam', 'content': 'x' * 500},
        )
        self.assertEqual(Testimonial.objects.count(), 0)

        self.client.post(
            reverse('admin_panel:add_testimonial'),
            {'title': 'Sarah Islam', 'content': 'Great to work with.'},
        )
        item = Testimonial.objects.get()
        self.assertEqual(item.title, 'Sarah Islam')

        self.client.post(reverse('admin_panel:delete_testimonial', args=[item.pk]))
        self.assertEqual(Testimonial.objects.count(), 0)

    def test_portfolio_hub_tabs_render_all_three_collections(self):
        Website_Portfolio.objects.create(title='Site', category='Website', technology='Django', link='https://a.test')
        Print_Design.objects.create(title='Print')
        Post_Design.objects.create(title='Post')

        for tab in ['website', 'print', 'post']:
            with self.subTest(tab=tab):
                response = self.client.get(reverse('admin_panel:portfolio_admin'), {'tab': tab})
                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.context['tab'], tab)

    def test_portfolio_search(self):
        Website_Portfolio.objects.create(title='Alpha', category='Website', technology='Django', link='https://a.test')
        Website_Portfolio.objects.create(title='Beta', category='Website', technology='Laravel', link='https://b.test')
        response = self.client.get(reverse('admin_panel:portfolio_admin'), {'q': 'alpha', 'tab': 'website'})
        self.assertEqual(len(response.context['website_portfolio']), 1)


class ClientLogoTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'pw')
        self.client.force_login(self.admin)

    def test_add_a_logo(self):
        response = self.client.post(
            reverse('admin_panel:add_client_logo'),
            {
                'title': 'Aurora',
                'link': 'aurora.test',
                'image': SimpleUploadedFile('logo.png', png_bytes(), content_type='image/png'),
            },
        )
        self.assertEqual(response.status_code, 302)
        logo = Client_Logo.objects.get()
        self.assertEqual(logo.title, 'Aurora')
        self.assertEqual(logo.target_url, 'https://aurora.test')

    def test_link_is_optional(self):
        self.client.post(
            reverse('admin_panel:add_client_logo'),
            {'title': 'No site', 'link': '', 'image': SimpleUploadedFile('logo.png', png_bytes())},
        )
        self.assertEqual(Client_Logo.objects.get().target_url, '')

    def test_edit_and_delete(self):
        self.client.post(
            reverse('admin_panel:add_client_logo'),
            {'title': 'Aurora', 'link': '', 'image': SimpleUploadedFile('logo.png', png_bytes())},
        )
        logo = Client_Logo.objects.get()

        self.client.post(reverse('admin_panel:update_client_logo', args=[logo.pk]), {'title': 'Aurora Two'})
        logo.refresh_from_db()
        self.assertEqual(logo.title, 'Aurora Two')

        response = self.client.get(reverse('admin_panel:delete_client_logo', args=[logo.pk]))
        self.assertEqual(response.status_code, 405)

        self.client.post(reverse('admin_panel:delete_client_logo', args=[logo.pk]))
        self.assertEqual(Client_Logo.objects.count(), 0)


class PricingCrudTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser('boss', 'boss@example.com', 'pw')
        self.client.force_login(self.admin)

    def _plan_payload(self, **overrides):
        payload = {
            'title': 'Starter',
            'tagline': 'For small businesses',
            'price': '$499',
            'period': '/project',
            'description': 'Everything you need to get online.',
            'features': '5-page website\nContact form\nBasic SEO',
            'cta_text': 'Get started',
            'cta_link': '',
            'order': '0',
            'is_active': 'on',
        }
        payload.update(overrides)
        return payload

    def test_create_a_plan(self):
        response = self.client.post(reverse('admin_panel:add_pricing'), self._plan_payload())
        self.assertRedirects(response, reverse('admin_panel:pricing'))
        plan = Pricing_Plan.objects.get()
        self.assertEqual(plan.title, 'Starter')
        self.assertTrue(plan.is_active)
        self.assertEqual(plan.feature_list, ['5-page website', 'Contact form', 'Basic SEO'])

    def test_title_and_price_are_required(self):
        self.client.post(reverse('admin_panel:add_pricing'), self._plan_payload(title='', price=''))
        self.assertEqual(Pricing_Plan.objects.count(), 0)

    def test_target_url_normalises_a_bare_domain(self):
        self.client.post(reverse('admin_panel:add_pricing'), self._plan_payload(cta_link='example.test'))
        self.assertEqual(Pricing_Plan.objects.get().target_url, 'https://example.test')

    def test_edit_and_delete(self):
        self.client.post(reverse('admin_panel:add_pricing'), self._plan_payload())
        plan = Pricing_Plan.objects.get()

        self.client.post(
            reverse('admin_panel:update_pricing', args=[plan.pk]),
            self._plan_payload(title='Starter Plus', price='$699'),
        )
        plan.refresh_from_db()
        self.assertEqual(plan.title, 'Starter Plus')
        self.assertEqual(plan.price, '$699')

        self.assertEqual(
            self.client.get(reverse('admin_panel:delete_pricing', args=[plan.pk])).status_code, 405
        )
        self.client.post(reverse('admin_panel:delete_pricing', args=[plan.pk]))
        self.assertEqual(Pricing_Plan.objects.count(), 0)

    def test_toggle_active(self):
        self.client.post(reverse('admin_panel:add_pricing'), self._plan_payload())
        plan = Pricing_Plan.objects.get()
        self.client.post(reverse('admin_panel:toggle_pricing_active', args=[plan.pk]))
        plan.refresh_from_db()
        self.assertFalse(plan.is_active)


class HomepagePricingTests(TestCase):
    def test_active_plans_render_on_the_homepage(self):
        Pricing_Plan.objects.create(title='Growth', price='$999', is_active=True)
        Pricing_Plan.objects.create(title='Hidden tier', price='$1', is_active=False)

        response = self.client.get(reverse('portfolio'))
        self.assertContains(response, 'Growth')
        self.assertNotContains(response, 'Hidden tier')

    def test_section_is_absent_without_active_plans(self):
        response = self.client.get(reverse('portfolio'))
        self.assertNotContains(response, 'id="pricing"')
