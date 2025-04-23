from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from faker import Faker
import random
from datetime import datetime
from inventory.models import ItemRequest, InventoryItem  # Adjust 'inventory' to your app's name

class Command(BaseCommand):
    help = 'Generate dummy data for ItemRequest model'

    def handle(self, *args, **kwargs):
        fake = Faker()
        users = list(User.objects.all())
        items = list(InventoryItem.objects.all())

        if not users or not items:
            self.stdout.write(self.style.ERROR('Please add some Users and InventoryItems first.'))
            return

        for _ in range(5000):  # You can adjust the number of records here
            user = random.choice(users)
            item = random.choice(items)
            status = random.choice([s[0] for s in ItemRequest.STATUS_CHOICES])
            
            # Generate request_date between 2020-01-01 and 2025-12-31
            request_date = fake.date_time_between(
                start_date=datetime(2020, 1, 1),
                end_date=datetime(2025, 3, 31)
            )
            
            # If the status is not 'pending', generate decision_date and return_date
            decision_date = fake.date_time_between(
                start_date=request_date,
                end_date=datetime(2025, 3, 31)
            ) if status != 'pending' else None

            issued_date = fake.date_time_between(
                start_date=decision_date,
                end_date=datetime(2025, 3, 31)
            ) if status == 'issued' else None
            
            

            return_date = fake.date_time_between(
                start_date=decision_date,
                end_date=datetime(2025, 3, 31)
            ) if status == 'returned' else None
            
            processed_by = random.choice(users) if status != 'pending' else None
            reason = fake.sentence() if status == 'rejected' else ''
            issued_by = random.choice(users) if status != 'issued' else None
            ItemRequest.objects.create(
                user=user,
                item=item,
                quantity=random.randint(1, 5),
                status=status,
                request_date=request_date,
                decision_date=decision_date,
                return_date=return_date,
                processed_by=processed_by,
                reason=reason,
                issued_date = issued_date,
                issued_by = issued_by
            )

        self.stdout.write(self.style.SUCCESS('✅ Dummy data created successfully.'))
