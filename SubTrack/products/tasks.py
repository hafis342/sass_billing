from django.utils import timezone
from celery import shared_task
from .models import Subscription, Invoice
from .utils import generate_invoice_pdf



@shared_task
def update_subcription_status():
    """
    Task to update the subscription status of customers
    """
    today = timezone.now().date()
    subcriptions = Subscription.objects.filter(
        status__in=('active', 'trialing')
        )
    for sub in subcriptions:
        if sub.status == 'trialing' and sub.trial_end_date <= today:
            sub.status = 'active'
        if not sub.plan.is_metered:
            if sub.status == 'active' and sub.end_date < today:
                sub.status = 'inactive'
        sub.save()

       
@shared_task
def generate_subscription_invoices():
    """
    Daily task to check for subscriptions due for billing
    """
    today = timezone.now().date()
    subscriptions = Subscription.objects.filter(
        end_date=today,
        status='active'
    )
    
    for subscription in subscriptions:
        create_invoice.delay(subscription.id)

@shared_task
def create_invoice(subscription_id):
    """
    Create invoice for a specific subscription
    """
    subscription = Subscription.objects.get(pk=subscription_id)
    
    invoice = Invoice.objects.create(
        customer=subscription.customer,
        subscription=subscription,
        amount=subscription.plan.price,
        status='unpaid',
        invoice_date=timezone.now().date(),
        due_date=timezone.now().date() + timezone.timedelta(days=15)
    )
    
    if generate_invoice_pdf(invoice):
        invoice.save()

       
# @shared_task
# def process_subscription_billing():
#     """
#     Daily task to handle subscription billing
#     """
#     today = timezone.now().date()
    
#     subscriptions = Subscription.objects.filter(
#         current_period_end=today,
#         status='active'
#     ).select_related('plan')
    
#     for subscription in subscriptions:
#         generate_invoice(subscription)
#         renew_subscription(subscription)