from io import BytesIO
from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
from django.conf import settings
import os
from django.utils import timezone
from datetime import timedelta, date
from .models import Invoice, UsageLog, Subscription


def generate_fixed_invoice(subscription):
    """
    Generate invoice for fixed-price subscription
    """
    invoice = Invoice.objects.create(
        customer=subscription.customer.user,
        subscription=subscription,
        amount=subscription.plan.price,
        status='unpaid',
        invoice_date=timezone.now().date(),
        due_date=timezone.now().date() + timedelta(days=15),
        pdf_url=' '
    )

    return invoice


def record_usage(
    subscription: Subscription,
    feature_name: str,
    quantity: int
    ) -> None:
    """
    Record usage log
    """
    UsageLog.objects.create(
        subscription=subscription,
        feature_name=feature_name,
        quantity=quantity,
        log_date=timezone.now().date(),
        is_billed=False
    )

   
def calculate_usage_charges(
    subscription: Subscription
    ) -> tuple[float, list[UsageLog]]:
    """
    Calculate total charges for usage between dates
    """
    if not subscription.plan.is_metered:
        raise ValueError("This plan is not usage-based")
    
    usage_logs = UsageLog.objects.filter(
        subscription=subscription,
        log_date__gte=subscription.start_date,
        log_date__lt=subscription.end_date,
        is_billed=False
    )
    
    total_charges = sum(
        record.quantity * subscription.plan.price_per_unit 
        for record in usage_logs
    )
        
    return total_charges, usage_logs


def generate_usage_invoice(subscription: Subscription) -> Invoice:
    """
    Generate invoice for usage-based subscription
    """
    total_amount, usage_logs = calculate_usage_charges(subscription)
    
    invoice = Invoice.objects.create(
        customer=subscription.customer.user,
        subscription=subscription,
        amount=total_amount,
        status='unpaid',
        invoice_date=timezone.now().date(),
        due_date=timezone.now().date() + timedelta(days=15),
        pdf_url=' '
    )
    usage_logs.update(is_billed=True)
    
    return invoice


def generate_invoice_pdf(invoice: Invoice) -> bool:
    """
    Generate PDF from HTML template and save to media storage
    """
    template_path = 'invoice.html'
    context = {
        'invoice': invoice,
        'customer': invoice.customer,
        'subscription': invoice.subscription
    }
    html_string = render_to_string(template_path, context)

    result = BytesIO()
    pdf = pisa.CreatePDF(BytesIO(html_string.encode("UTF-8"), result))
    
    if not pdf.err:
        # Save to media storage
        filename = f"invoices/invoice_{invoice.id}_{invoice.invoice_date}.pdf"
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        
        with open(filepath, 'wb') as f:
            f.write(result.getvalue())
        
        # Update invoice with PDF URL
        invoice.pdf_url = os.path.join(settings.MEDIA_URL, filename)
        invoice.save()
        return True
    
    return False