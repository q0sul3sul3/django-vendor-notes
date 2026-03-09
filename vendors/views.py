from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Vendor, Note
import pandas as pd
import os
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import openpyxl
from openpyxl import Workbook
from io import BytesIO
import re


def vendor_list(request):
    vendors = Vendor.objects.all()
    return render(request, "vendors/vendor_list.html", {"vendors": vendors})


def vendor_detail(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    notes = vendor.notes.all()
    return render(
        request, "vendors/vendor_detail.html", {"vendor": vendor, "notes": notes}
    )


def vendor_create(request):
    error_message = None
    if request.method == "POST":
        name = request.POST["name"]
        contact_email = request.POST["contact_email"]
        phone = request.POST["phone"]

        # Validate phone number
        if not re.match(r"^[\d\-\(\)\+]+$", phone):
            error_message = (
                "Phone number can only contain numbers and symbols (-, (, ), +)."
            )
        else:
            Vendor.objects.create(name=name, contact_email=contact_email, phone=phone)
            return redirect("vendor_list")

    return render(request, "vendors/vendor_form.html", {"error_message": error_message})


def vendor_edit(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    error_message = None

    # 獲取 next 參數，決定跳轉目標
    next_page = request.GET.get("next", "detail")

    if request.method == "POST":
        name = request.POST["name"]
        contact_email = request.POST["contact_email"]
        phone = request.POST["phone"]
        next_page = request.POST.get("next", next_page)  # 從 POST 獲取，如果有的話

        # Validate phone number
        if not re.match(r"^[\d\-\(\)\+]+$", phone):
            error_message = (
                "Phone number can only contain numbers and symbols (-, (, ), +)."
            )
        else:
            vendor.name = name
            vendor.contact_email = contact_email
            vendor.phone = phone
            vendor.save()
            if next_page == "list":
                return redirect("vendor_list")
            else:
                return redirect("vendor_detail", pk=vendor.pk)

    return render(
        request,
        "vendors/vendor_form.html",
        {"vendor": vendor, "error_message": error_message, "next": next_page},
    )


def vendor_delete(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    if request.method == "POST":
        vendor.delete()
        return redirect("vendor_list")
    return render(request, "vendors/vendor_confirm_delete.html", {"vendor": vendor})


def note_create(request, vendor_pk):
    vendor = get_object_or_404(Vendor, pk=vendor_pk)
    if request.method == "POST":
        title = request.POST["title"]
        content = request.POST["content"]
        Note.objects.create(vendor=vendor, title=title, content=content)
        return redirect("vendor_detail", pk=vendor.pk)
    return render(request, "vendors/note_form.html", {"vendor": vendor})


def note_edit(request, pk):
    note = get_object_or_404(Note, pk=pk)
    if request.method == "POST":
        note.title = request.POST["title"]
        note.content = request.POST["content"]
        note.save()
        return redirect("vendor_detail", pk=note.vendor.pk)
    return render(request, "vendors/note_form.html", {"note": note})


def note_delete(request, pk):
    note = get_object_or_404(Note, pk=pk)
    vendor_pk = note.vendor.pk
    if request.method == "POST":
        note.delete()
        return redirect("vendor_detail", pk=vendor_pk)
    return render(request, "vendors/note_confirm_delete.html", {"note": note})


def export_excel(request):
    vendors = Vendor.objects.all()
    notes = Note.objects.all()

    wb = Workbook()
    ws1 = wb.active
    ws1.title = "Vendors"
    ws1.append(["ID", "Name", "Contact Email", "Phone"])
    for vendor in vendors:
        ws1.append([vendor.id, vendor.name, vendor.contact_email, vendor.phone])

    ws2 = wb.create_sheet("Notes")
    ws2.append(["ID", "Vendor", "Title", "Content", "Date"])
    for note in notes:
        ws2.append(
            [
                note.id,
                note.vendor.name,
                note.title,
                note.content,
                note.date.replace(tzinfo=None) if note.date else None,
            ]
        )

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = "attachment; filename=vendors_notes.xlsx"
    return response


def import_vendors_csv(request):
    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        folder_path = request.POST.get("folder_path", "uploads")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, csv_file.name)
        with open(file_path, "wb+") as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)

        df = pd.read_csv(file_path)
        errors = []
        for index, row in df.iterrows():
            try:
                if "name" in row and "contact_email" in row and "phone" in row:
                    # Validate phone number
                    if not re.match(r"^[\d\-\(\)\+]+$", str(row["phone"])):
                        errors.append(f"Row {index}: Invalid phone number format")
                        continue
                    # Vendor: update if exists (by name), create if not
                    vendor, created = Vendor.objects.get_or_create(
                        name=row["name"],
                        defaults={
                            "contact_email": row["contact_email"],
                            "phone": row["phone"],
                        },
                    )
                    if not created:
                        vendor.contact_email = row["contact_email"]
                        vendor.phone = row["phone"]
                        vendor.save()
                else:
                    errors.append(
                        f"Row {index}: Missing required fields (name, contact_email, phone)"
                    )
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")

        return render(request, "vendors/import_result.html", {"errors": errors, "import_type": "vendors"})
    return render(request, "vendors/import_csv.html", {"import_type": "vendors"})


def import_notes_csv(request):
    if request.method == "POST":
        csv_file = request.FILES["csv_file"]
        folder_path = request.POST.get("folder_path", "uploads")
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        file_path = os.path.join(folder_path, csv_file.name)
        with open(file_path, "wb+") as destination:
            for chunk in csv_file.chunks():
                destination.write(chunk)

        df = pd.read_csv(file_path)
        errors = []
        for index, row in df.iterrows():
            try:
                if "vendor" in row and "title" in row and "content" in row:
                    # Note: update if exists (by vendor and title), create if not
                    try:
                        vendor = Vendor.objects.get(name=row["vendor"])
                        note, created = Note.objects.get_or_create(
                            vendor=vendor,
                            title=row["title"],
                            defaults={"content": row["content"]},
                        )
                        if not created:
                            note.content = row["content"]
                            note.save()
                    except Vendor.DoesNotExist:
                        errors.append(
                            f"Row {index}: Vendor '{row['vendor']}' does not exist"
                        )
                else:
                    errors.append(
                        f"Row {index}: Missing required fields (vendor, title, content)"
                    )
            except Exception as e:
                errors.append(f"Row {index}: {str(e)}")

        return render(request, "vendors/import_result.html", {"errors": errors, "import_type": "notes"})
    return render(request, "vendors/import_csv.html", {"import_type": "notes"})
