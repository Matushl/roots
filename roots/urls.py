from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.views.generic import TemplateView
from base.views import IndexView
from django.conf import settings
from django.conf.urls.static import static

admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'roots.views.home', name='home'),
    # url(r'^roots/', include('roots.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^accounts/profile/', TemplateView.as_view(
                               template_name='profile.html')),
    url(r'^competitions/', include('competitions.urls')),
    url(r'^comments/', include('django.contrib.comments.urls')),
    url(r'^problems/', include('problems.urls')),
    url(r'^posts/', include('posts.urls')),
    url(r'^photos/', include('photologue.urls')),
    url(r'^profiles/', include('profiles.urls')),
    url(r'^$', IndexView.as_view(), name='roots_index'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
