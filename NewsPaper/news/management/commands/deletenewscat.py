import sys
from django.core.management.base import BaseCommand
from news.models import Category, Post


class Command(BaseCommand):
    help = "Удалить новости определенной категории"

    def add_arguments(self, parser):
        parser.add_argument('category', type=str)

    def handle(self, *args, **options):
        category_name = options['category']
        self.stdout.write(f'Вы правда хотите удалить все статьи в категории "{category_name}"? yes/no: ')
        answer = input()  # Читаем ввод

        if answer.lower() != 'yes':
            self.stdout.write(self.style.ERROR('Операция отменена'))
            return

        try:
            # Получаем категорию
            category = Category.objects.get(name=category_name)

            # Удаляем связанные посты
            Post.objects.filter(categories=category).delete()

            self.stdout.write(self.style.SUCCESS(f'Успешно удалены все статьи из категории "{category_name}"'))
        except Category.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Категория "{category_name}" не найдена'))
