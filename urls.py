from django.urls import path

from . import views

urlpatterns = [
    path('enlaces/', views.all_links),
    path('enlaces/process/', views.get_queued_links),
    path('enlaces/posted/<int:url>', views.set_link_queued),
    path('server/time', views.server_time),


]