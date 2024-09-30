from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

#adaugare cai pentru site
urlpatterns = [
    path("signup/", views.signup, name = "signup"),
    path("home/", views.home, name = "home"),
    path("faq/", views.faq, name = "faq"),
    path("explore/", views.explore, name = "explore"),
    path("featuredToday/", views.featuredToday, name = "featuredToday"),
    path('film/<str:film_title>/', views.film_detail, name='film_detail'),
    path('film/<str:film_title>/add_review/', views.add_review, name='add_review'),
    path('search_movies/', views.searchMovies, name='search_movies'),
    path('user/', views.userPage, name='user_page'),
    path('actor/<str:actor_name>/', views.actor_detail, name='actor_detail'),
    path('add_to_favorites/', views.add_to_favorites, name='add_to_favorites'),
    path('remove_from_favorites/', views.remove_from_favorites, name='remove_from_favorites'),
    path('change-password/', auth_views.PasswordChangeView.as_view(), name='change_password'),
    path('delete-account/', views.delete_account, name='delete_account'),
    path('film-criteria-form/', views.film_help, name='film_help'),
    path('films/<str:search_term>/', views.film_suggestions, name='film_suggestions'),
    path('subscribe/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('unsubscribe/', views.unsubscribe_newsletter, name='unsubscribe_newsletter'),
    path('gdpr/', views.gdpr, name='gdpr'),
    path('blog/', views.blog, name='blog'),
    path('timeline/', views.timeline, name='timeline'),
    path('evolution/', views.evolution, name='evolution'),
    path('milestones/', views.milestones, name='milestones'),
    path('locations/', views.locations, name='locations'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)