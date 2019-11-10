from django.conf.urls import url
from catalog import views

urlpatterns = [
    url(r'^search/$', views.search, name='search'),
    url(r'^product/(?P<product_id>[0-9]+)/$', views.list_substitute, name='list_substitute'),
    url(r'^substitute/(?P<substitute_id>[0-9]+)/$', views.detail_substitute, name='detail_substitute'),
    url(r'^legal/$', views.legal, name='legal'),
    url(r'^categories/$', views.list_categories, name='list_categories'),
    url(r'^products/$', views.list_products, name='list_products'),
]