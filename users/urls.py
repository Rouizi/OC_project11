from django.conf.urls import url
from users import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^log_in/$', views.log_in, name='log_in'),
    url(r'^log_out/$', views.log_out, name="log_out"),
    url(r'^profile/$', views.profile, name='profile'),
    url(r'^save_product/(?P<sub_id>[0-9]+)/$', views.save_product, name='save_product'),
    url(r'^list_saved_products/$', views.list_saved_products, name='list_saved_products'),
    url(r'^password_reset/$', auth_views.PasswordResetView.as_view(
        template_name='users/password_reset_form.html', email_template_name='users/password_reset_email.html',
        subject_template_name='users/password_reset_subject.txt', success_url='/users/password_reset/done/'),
        name='password_reset'),
    url(r'^password_reset/done/$', auth_views.PasswordResetDoneView.as_view(
        template_name='users/password_reset_done.html'), name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        auth_views.PasswordResetConfirmView.as_view(
            template_name='users/password_reset_confirm.html', success_url='/users/reset/done/'),
        name='password_reset_confirm'),
    url(r'^reset/done/$', auth_views.PasswordResetCompleteView.as_view(
        template_name='users/password_reset_complete.html'), name='password_reset_complete'),
]