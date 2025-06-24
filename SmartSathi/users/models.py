from django.db import models
from django.contrib.auth.models import User

class BookkeepingEntry(models.Model):
    TRANSACTION_TYPE = (
        ('income', 'Income'),
        ('expense', 'Expense'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    description = models.TextField()
    type = models.CharField(max_length=10, choices=TRANSACTION_TYPE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=100, blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.type} - ₹{self.amount} on {self.date}"
