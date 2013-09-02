from django.conf.urls import patterns, include, url
import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'soccer.views.home', name='home'),
    # url(r'^soccer/', include('soccer.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'^$','app.views.index', name="home"),
    url(r'^data/$', 'app.views.data', name="data"),
    url(r'^players/$', "app.views.players", name="players"),
    url(r'^users/$', "app.views.users", name="users"),
    url(r'^recordaction/$', "app.views.record_action", name="record_action"),
    url(r'^clean/$', "app.views.clean", name="clean"),
    url(r'^join/$', "app.views.join", name="join"),
    url(r'^selectplayer/$', "app.views.selectplayer", name="select_player"),
    url(r'^dropplayer/$', "app.views.dropplayer", name="drop_player"),
    url(r'^currentplayers/$', 'app.views.currentplayers', name='current_players')
)

urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.STATIC_ROOT}),
    )
