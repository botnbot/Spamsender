from django.urls import path

from core.views import (MessageListView, MessageDetailView, MessageCreateView, MessageUpdateView, MessageDeleteView,
                        RecipientListView, RecipientDetailView, RecipientCreateView, RecipientUpdateView,
                        RecipientDeleteView,
                        NewsletterListView, NewsletterDetailView, NewsletterCreateView, NewsletterUpdateView,
                        NewsletterManualSendView,
                        NewsletterDeleteView, ActiveNewsletterListView,
                        SendAttemptListView, SendAttemptDetailView, FailedSendAttemptListView,
                        SuccessfulSendAttemptListView)
from .views import HomeView

app_name = 'core'

urlpatterns = [
    path("", HomeView.as_view(), name="home"),

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

    path('active_newsletter/', ActiveNewsletterListView.as_view(), name='active_newsletter_list'),
    path('newsletter/', NewsletterListView.as_view(), name='newsletter_list'),
    path('newsletter/<int:pk>/', NewsletterDetailView.as_view(), name='newsletter_detail'),
    path('newsletter/new/', NewsletterCreateView.as_view(), name='newsletter_create'),
    path('newsletter/<int:pk>/edit/', NewsletterUpdateView.as_view(), name='newsletter_update'),
    path('newsletter/<int:pk>/delete/', NewsletterDeleteView.as_view(), name='newsletter_delete'),
    path("newsletter/<int:pk>/send/", NewsletterManualSendView.as_view(), name="newsletter_manual_send"),

    path("attempts/", SendAttemptListView.as_view(), name="attempt_list"),
    path("attempts/<int:pk>/", SendAttemptDetailView.as_view(), name="attempt_detail"),
    path("attempts/success/", SuccessfulSendAttemptListView.as_view(), name="success_attempt_list"),
    path("attempts/fail/", FailedSendAttemptListView.as_view(), name="fail_attempt_list"),

    # path("attempts/<int:pk>/edit/", SendAttemptUpdateView.as_view(), name="attempt_update"),
    # path("attempts/<int:pk>/delete/", SendAttemptDeleteView.as_view(), name="attempt_confirm_delete"),
    # path("attempts/new/", SendAttemptCreateView.as_view(), name="attempt_create"),
]
