from __future__ import annotations

from django.contrib import messages
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_GET, require_http_methods

import data_store as store


def _admin_ok(request: HttpRequest) -> bool:
    return bool(request.session.get("demo_admin"))


def _require_admin(request: HttpRequest) -> HttpResponse | None:
    if not _admin_ok(request):
        messages.error(request, "Administrator access required.")
        return redirect("portal:admin_login")
    return None


@require_GET
def home(request: HttpRequest) -> HttpResponse:
    return render(request, "home.html")


@require_http_methods(["GET", "POST"])
def request_form(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        doc = (request.POST.get("document_type") or "").strip()
        full_name = request.POST.get("full_name") or ""
        address = request.POST.get("address") or ""
        purpose = request.POST.get("purpose") or ""
        contact = request.POST.get("contact") or ""
        bhw = request.POST.get("bhw_officer") or ""

        errors: list[str] = []
        if doc not in store.DOCUMENT_LABELS:
            errors.append("Select a valid document type.")
        if not full_name.strip():
            errors.append("Full name is required.")
        if not purpose.strip():
            errors.append("Purpose or notes are required.")
        if not contact.strip():
            errors.append("Contact number is required.")
        if doc == "health" and not bhw.strip():
            errors.append("BHW officer assigned is required for Health Certification.")

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(
                request,
                "request_form.html",
                {
                    "posted": {
                        "document_type": doc,
                        "full_name": full_name,
                        "address": address,
                        "purpose": purpose,
                        "contact": contact,
                        "bhw_officer": bhw,
                    }
                },
            )

        record = store.add_request(
            document_type=doc,
            full_name=full_name,
            address=address,
            purpose=purpose,
            contact=contact,
            bhw_officer=bhw,
        )
        messages.success(
            request,
            f"Request submitted. Your reference number is {record['reference']}. "
            "Please save it for tracking.",
        )
        return redirect("portal:tracker")

    return render(request, "request_form.html", {"posted": {}})


@require_http_methods(["GET", "POST"])
def tracker(request: HttpRequest) -> HttpResponse:
    ref = ""
    result = None
    if request.method == "POST":
        ref = (request.POST.get("reference") or "").strip()
        if not ref:
            messages.error(request, "Enter a reference number.")
        else:
            found = store.get_by_reference(ref)
            if found is None:
                messages.warning(request, "No request found for that reference number.")
            else:
                result = found
                result["document_label"] = store.DOCUMENT_LABELS.get(
                    result["document_type"],
                    result["document_type"],
                )
    return render(
        request,
        "tracker.html",
        {"reference_query": ref, "result": result},
    )


@require_http_methods(["GET", "POST"])
def admin_login(request: HttpRequest) -> HttpResponse:
    if _admin_ok(request):
        return redirect("portal:admin_dash")

    if request.method == "POST":
        user = (request.POST.get("username") or "").strip()
        pwd = request.POST.get("password") or ""
        if user == "admin" and pwd == "admin":
            request.session["demo_admin"] = True
            messages.success(request, "Signed in as administrator.")
            return redirect("portal:admin_dash")
        messages.error(request, "Invalid username or password.")

    return render(request, "admin_login.html")


@require_GET
def admin_logout(request: HttpRequest) -> HttpResponse:
    request.session.pop("demo_admin", None)
    messages.info(request, "Signed out.")
    return redirect("portal:admin_login")


@require_http_methods(["GET", "POST"])
def admin_dash(request: HttpRequest) -> HttpResponse:
    block = _require_admin(request)
    if block:
        return block

    if request.method == "POST":
        action = (request.POST.get("action") or "").strip()
        if action == "delete_all":
            n = store.delete_all()
            messages.warning(request, f"Cleared {n} demo record(s).")
            return redirect("portal:admin_dash")

        rid_raw = request.POST.get("record_id")
        try:
            rid = int(rid_raw)
        except (TypeError, ValueError):
            messages.error(request, "Invalid record.")
            return redirect("portal:admin_dash")

        if action == "approve":
            ok = store.set_status(rid, store.STATUS_APPROVED)
            if ok:
                messages.success(request, "Marked as approved.")
            else:
                messages.error(request, "Record not found.")
        elif action == "reject":
            ok = store.set_status(rid, store.STATUS_REJECTED)
            if ok:
                messages.success(request, "Marked as rejected.")
            else:
                messages.error(request, "Record not found.")
        elif action == "ready":
            ok = store.set_status(rid, store.STATUS_READY)
            if ok:
                messages.success(request, "Marked as ready for pickup.")
            else:
                messages.error(request, "Record not found.")
        else:
            messages.error(request, "Unknown action.")
        return redirect("portal:admin_dash")

    rows = store.list_requests()
    for r in rows:
        r["document_label"] = store.DOCUMENT_LABELS.get(
            r["document_type"],
            r["document_type"],
        )
    return render(request, "admin_dash.html", {"rows": rows})
