from django.urls import path
from . import views

urlpatterns = [
    path("", views.vendor_list, name="vendor_list"),
    path("vendor/<int:pk>/", views.vendor_detail, name="vendor_detail"),
    path("vendor/new/", views.vendor_create, name="vendor_create"),
    path("vendor/<int:pk>/edit/", views.vendor_edit, name="vendor_edit"),
    path("vendor/<int:pk>/delete/", views.vendor_delete, name="vendor_delete"),
    path("vendor/<int:vendor_pk>/note/new/", views.note_create, name="note_create"),
    path("note/<int:pk>/edit/", views.note_edit, name="note_edit"),
    path("note/<int:pk>/delete/", views.note_delete, name="note_delete"),
    path("export/", views.export_excel, name="export_excel"),
    path("import/vendors/", views.import_vendors_csv, name="import_vendors_csv"),
    path("import/notes/", views.import_notes_csv, name="import_notes_csv"),
]
