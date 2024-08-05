from django.urls import path

from . import views


urlpatterns = [
    #Main
    path("", views.index, name="index"),

    #Actions

    path('create-report/', views.generate_pdf, name='create_report'),

    path('assign_pallet/', views.assign_pallet, name = 'assign_pallet'),

    path('add_to_rack/', views.add_to_rack, name = 'add_to_rack'),

    path('create_pallet/', views.create_pallet, name='create_pallet'),

    path('update_cargo/<str:sku>/update', views.update_cargo, name='update_cargo'),

    #Database

    path('cargo/<str:sku>/',views.cargo_details, name = 'cargo_details'),

    path('assigned_pallets/', views.assigned_pallets, name = 'assigned_pallets'),

    path('rack_places/', views.rack_places, name = 'rack_places'),
    
    path('all-report', views.create_whole_report, name = 'all_report'),

    path('list/', views.ware_list_view, name='ware_list'),

    path('search/', views.search, name='search'),

    path('pallet_list/', views.pallet_list, name='pallet_list'),

    
]