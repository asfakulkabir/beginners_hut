"""Routes for the custom admin panel.

Namespaced as ``admin_panel:`` on purpose. The public site already owns plain
names like ``blog`` and ``portfolio``; without a namespace the admin's
``blog`` route silently reversed to the public ``/blog/`` list.

Paths are unchanged from the previous version where a route already existed
(``/admin/blog/``, ``/admin/contact_message/``, ``/admin/add_post_design/`` …) so
existing bookmarks keep working. Update routes and the two new collections
(client logos, message read state) are additive.

Deletes are POST-only, enforced by ``@require_POST`` in the views.
"""

from django.urls import path

from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.admin_login, name='admin_login'),
    path('login/', views.admin_login, name='admin_login_alias'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('dashboard/', views.dashboard, name='dashboard'),
    # contact inbox
    path('contact_message/', views.contact_message, name='contact_message'),
    path('toggle_contact_read/<int:pk>/', views.toggle_contact_read, name='toggle_contact_read'),
    path('delete_contact/<int:pk>/', views.delete_contact, name='delete_contact'),
    # blog
    path('blog/', views.blog, name='blog'),
    path('add_blog/', views.add_blog, name='add_blog'),
    path('update_blog/<int:pk>/', views.update_blog, name='update_blog'),
    path('toggle_blog_published/<int:pk>/', views.toggle_blog_published, name='toggle_blog_published'),
    path('delete_blog/<int:pk>/', views.delete_blog, name='delete_blog'),
    # portfolio
    path('portfolio_admin/', views.portfolio_admin, name='portfolio_admin'),
    path('add_print_design/', views.add_print_design, name='add_print_design'),
    path('update_print_design/<int:pk>/', views.update_print_design, name='update_print_design'),
    path('delete_print_design/<int:pk>/', views.delete_print_design, name='delete_print_design'),
    path('add_post_design/', views.add_post_design, name='add_post_design'),
    path('update_post_design/<int:pk>/', views.update_post_design, name='update_post_design'),
    path('delete_post_design/<int:pk>/', views.delete_post_design, name='delete_post_design'),
    path('add_website_portfolio/', views.add_website_portfolio, name='add_website_portfolio'),
    path('update_website_portfolio/<int:pk>/', views.update_website_portfolio, name='update_website_portfolio'),
    path('delete_website_portfolio/<int:pk>/', views.delete_website_portfolio, name='delete_website_portfolio'),
    # testimonials
    path('testimonial/', views.testimonial, name='testimonial'),
    path('add_testimonial/', views.add_testimonial, name='add_testimonial'),
    path('update_testimonial/<int:pk>/', views.update_testimonial, name='update_testimonial'),
    path('delete_testimonial/<int:pk>/', views.delete_testimonial, name='delete_testimonial'),
    # client logos
    path('client_logo/', views.client_logo, name='client_logo'),
    path('add_client_logo/', views.add_client_logo, name='add_client_logo'),
    path('update_client_logo/<int:pk>/', views.update_client_logo, name='update_client_logo'),
    path('delete_client_logo/<int:pk>/', views.delete_client_logo, name='delete_client_logo'),
    # pricing
    path('pricing/', views.pricing, name='pricing'),
    path('add_pricing/', views.add_pricing, name='add_pricing'),
    path('update_pricing/<int:pk>/', views.update_pricing, name='update_pricing'),
    path('toggle_pricing_active/<int:pk>/', views.toggle_pricing_active, name='toggle_pricing_active'),
    path('delete_pricing/<int:pk>/', views.delete_pricing, name='delete_pricing'),
]
