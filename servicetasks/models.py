from django.db import models
from django.conf import settings
from usermanagement.models import ServiceRequest, Users  # Adjust if in a different app


class ServiceTask(models.Model):
    STATUS_CHOICES = [
        ('yet to be started', 'Yet to be Started'),
        ('in progress', 'In Progress'),
        ('completed', 'Completed'),
        ('sent for approval', 'Sent for Approval'),
        ('revoked', 'Revoked'),
    ]
    PRIORITY_STATUS_CHOICES = [
        ('critical', 'Critical'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('high', 'High'),
    ]

    service_request = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='service_tasks')
    service_type = models.CharField(max_length=50)
    category_name = models.CharField(max_length=100)

    client = models.ForeignKey(Users, on_delete=models.CASCADE, related_name='client_service_tasks')
    assignee = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='assigned_service_tasks')
    reviewer = models.ForeignKey(Users, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name='reviewed_service_tasks')

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in progress')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    due_date = models.DateField(default=None, null=True)
    priority = models.CharField(max_length=20, choices=PRIORITY_STATUS_CHOICES, default='low')
    completion_percentage = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.service_type} - {self.category_name} (Request #{self.service_request.id})"

