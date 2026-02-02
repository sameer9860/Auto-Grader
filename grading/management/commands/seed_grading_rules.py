"""
Management command to seed Nepal grading scale rules
"""

from django.core.management.base import BaseCommand
from grading.models import GradingRule
from decimal import Decimal


class Command(BaseCommand):
    help = 'Seeds the database with Nepal grading scale rules'

    def handle(self, *args, **options):
        self.stdout.write('Seeding Nepal grading scale rules...')
        
        # Nepal grading scale
        grades = [
            {
                'grade': 'A+',
                'min_percentage': Decimal('90.00'),
                'max_percentage': Decimal('100.00'),
                'gpa': Decimal('4.00'),
                'description': 'Outstanding'
            },
            {
                'grade': 'A',
                'min_percentage': Decimal('80.00'),
                'max_percentage': Decimal('89.99'),
                'gpa': Decimal('3.60'),
                'description': 'Excellent'
            },
            {
                'grade': 'B+',
                'min_percentage': Decimal('70.00'),
                'max_percentage': Decimal('79.99'),
                'gpa': Decimal('3.20'),
                'description': 'Very Good'
            },
            {
                'grade': 'B',
                'min_percentage': Decimal('60.00'),
                'max_percentage': Decimal('69.99'),
                'gpa': Decimal('2.80'),
                'description': 'Good'
            },
            {
                'grade': 'C+',
                'min_percentage': Decimal('50.00'),
                'max_percentage': Decimal('59.99'),
                'gpa': Decimal('2.40'),
                'description': 'Satisfactory'
            },
            {
                'grade': 'C',
                'min_percentage': Decimal('40.00'),
                'max_percentage': Decimal('49.99'),
                'gpa': Decimal('2.00'),
                'description': 'Acceptable'
            },
            {
                'grade': 'D',
                'min_percentage': Decimal('32.00'),
                'max_percentage': Decimal('39.99'),
                'gpa': Decimal('1.60'),
                'description': 'Partially Acceptable'
            },
            {
                'grade': 'E',
                'min_percentage': Decimal('20.00'),
                'max_percentage': Decimal('31.99'),
                'gpa': Decimal('0.80'),
                'description': 'Insufficient'
            },
            {
                'grade': 'NG',
                'min_percentage': Decimal('0.00'),
                'max_percentage': Decimal('19.99'),
                'gpa': Decimal('0.00'),
                'description': 'Not Graded'
            },
        ]
        
        created_count = 0
        updated_count = 0
        
        for grade_data in grades:
            rule, created = GradingRule.objects.update_or_create(
                grade=grade_data['grade'],
                defaults={
                    'min_percentage': grade_data['min_percentage'],
                    'max_percentage': grade_data['max_percentage'],
                    'gpa': grade_data['gpa'],
                    'description': grade_data['description'],
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created grading rule: {rule.grade}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'Updated grading rule: {rule.grade}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\nCompleted! Created: {created_count}, Updated: {updated_count}'
            )
        )
