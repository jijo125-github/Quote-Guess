from django.urls import path,re_path
from django.conf.urls import url
from gameapp import views

app_name ='gameapp'
urlpatterns=[
    path('',views.home,name='home'),
    path('game/',views.game,name='game'),
    path('scrape/',views.scrape,name='scraper'),
    path('actualgame/',views.actualgame,name='actualgame'),
    re_path(r'^quotes/(?P<author>[\w|\W]+)/$',views.quotesbyauthor,name='authorquotes'),
]
