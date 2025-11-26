from django.urls import path

from core.views import *

app_name = 'core'

urlpatterns = [
    path('message/', MessageListView.as_view(), name='message_list'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message/new/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/edit/', MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),

    path('recipient/', RecipientListView.as_view(), name='recipient_list'),
    path('recipient/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipient/new/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/edit/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),

    path('newsletter/', NewsletterListView.as_view(), name='newsletter_list'),
    path('newsletter/<int:pk>/', NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('newsletter/new/', NewsletterCreateView.as_view(), name='newsletter_create'),
    path('newsletter/<int:pk>/edit/', NewsletterUpdateView.as_view(), name='newsletter_update'),
    path('newsletter/<int:pk>/delete/', NewsletterDeleteView.as_view(), name='newsletter_delete'),

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    ]

