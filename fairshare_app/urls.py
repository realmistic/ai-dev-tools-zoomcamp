from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create/', views.create_group, name='create_group'),
    path('group/<int:group_id>/', views.group_detail, name='group_detail'),
    path('group/<int:group_id>/add-person/', views.add_person, name='add_person'),
    path('group/<int:group_id>/add-expense/', views.add_expense, name='add_expense'),
]
