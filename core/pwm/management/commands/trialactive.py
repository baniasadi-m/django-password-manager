from django.utils import timezone
from datetime import timedelta, time
from django.core.management.base import BaseCommand
from ...models import LicenseInfo, WorkingHours
from sys import exit

class Command(BaseCommand):
    help = "Create trial license and working time"

    def handle(self, *args, **options):
        try:
            # Fetch all LicenseInfo objects
            license = LicenseInfo.objects.all()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Database fetch error: {e}"))
            exit(3)


        try:
            # Calculate the expiration date (30 days from now)
            expire_date = timezone.now() + timedelta(days=30)

            # Input data for creating a new LicenseInfo entry
            input_data = {
                'company_short_name': 'trial',
                'company_name': 'trial',
                'limit_user': 50,
                'expired_at': expire_date,
                'api_enabled': True
            }

            # Create the new LicenseInfo entry
            license = LicenseInfo.objects.create(**input_data)
            self.stdout.write(self.style.SUCCESS(f"Successfully created LicenseInfo with ID: {license.id}"))

            # Update latest_check field
            license.latest_check = timezone.now()
            license.save(update_fields=['latest_check'])

            # Create and save the WorkingHours entry
            work_time = WorkingHours(
                start_time=time(0, 26, 0),
                end_time=time(23, 26, 0),
                weekdays="0,1,2,3,4,5,6"
            )
            work_time.save()
            self.stdout.write(self.style.SUCCESS(f"Successfully created WorkingHours with ID: {work_time.id}"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Database update error: {e}"))
            exit(2)
