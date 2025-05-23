from django.urls import path
from . import views

app_name = 'librarians'

urlpatterns = [
    path('upload/', views.upload_item, name='upload'),
    path('view_items/', views.view_items, name='view_items'),
    path('collection/', views.create_collections, name='collection'),
]
