from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home_view, name='home'),
    path('', views.landing_view, name='landing'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('chatbot/', views.chatbot_view, name='chatbot'),
    path('bookkeeping/', views.bookkeeping_view, name='bookkeeping'),
    path('market-prices/', views.market_prices_view, name='market_prices'),
    path('livestock-tips/', views.livestock_tips_view, name='livestock_tips'),
    path('chatbot-api/', views.chatbot_api, name='chatbot_api'),
]