from django.urls import path, include


from .views import (
    CommentDetailView,
    CommentDeleteView,
)


urlpatterns = [
    path('<int:pk>/', CommentDetailView.as_view(), name='thread'),
    path('<int:pk>/delete/', CommentDeleteView.as_view(), name='comment_delete'),
]
