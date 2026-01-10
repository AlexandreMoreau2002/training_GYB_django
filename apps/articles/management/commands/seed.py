import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from apps.articles.models import Article, Category, Comment, Tag

fake = Faker('fr_FR')


class Command(BaseCommand):
    help = 'Seed the database with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before seeding',
        )

    def handle(self, *args, **options):
        if options['clear']:
            self.stdout.write('Clearing existing data...')
            Comment.objects.all().delete()
            Article.objects.all().delete()
            Tag.objects.all().delete()
            Category.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        self.create_categories()
        self.create_tags()
        self.create_users()
        self.create_articles()
        self.create_comments()

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))

    def create_categories(self):
        categories = [
            {'name': 'Bloc', 'description': 'Escalade sur blocs de faible hauteur sans corde'},
            {'name': 'Voie', 'description': 'Escalade en falaise avec corde et assurage'},
            {'name': 'Grande Voie', 'description': 'Escalade de parois de plusieurs longueurs'},
            {'name': 'Alpinisme', 'description': 'Ascensions en haute montagne'},
        ]
        for cat in categories:
            Category.objects.get_or_create(name=cat['name'], defaults={'description': cat['description']})
        self.stdout.write(f'  Created {len(categories)} categories')

    def create_tags(self):
        tags = [
            'Débutant', 'Intermédiaire', 'Expert',
            'Technique', 'Force', 'Endurance',
            'Sécurité', 'Matériel', 'Entraînement',
            'Compétition', 'Outdoor', 'Indoor',
            'Falaise', 'Montagne', 'Salle',
        ]
        for tag_name in tags:
            Tag.objects.get_or_create(name=tag_name)
        self.stdout.write(f'  Created {len(tags)} tags')

    def create_users(self):
        # Create admin if doesn't exist
        if not User.objects.filter(username='admin').exists():
            admin = User.objects.create_superuser(
                username='admin',
                email='admin@summit.local',
                password='admin123',
                first_name='Admin',
                last_name='Summit'
            )
            admin.profile.bio = 'Administrateur du blog Summit'
            admin.profile.save()
            self.stdout.write('  Created admin user (admin/admin123)')

        # Create regular users
        users_created = 0
        for i in range(5):
            username = f'user{i+1}'
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@summit.local',
                    password='password123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                user.profile.bio = fake.paragraph(nb_sentences=2)
                user.profile.website = fake.url() if random.random() > 0.5 else ''
                user.profile.save()
                users_created += 1
        self.stdout.write(f'  Created {users_created} regular users')

    def create_articles(self):
        categories = list(Category.objects.all())
        tags = list(Tag.objects.all())
        authors = list(User.objects.all())

        climbing_titles = [
            "Comment débuter l'escalade en salle",
            "Les meilleures falaises de France",
            "Améliorer sa technique de pied",
            "Le matériel essentiel pour grimper",
            "Entraînement de force pour grimpeurs",
            "Sécurité en grande voie : les bases",
            "Mon premier 7a : retour d'expérience",
            "Les compétitions de bloc en 2025",
            "Grimper en extérieur vs en salle",
            "La préparation mentale en escalade",
            "Les meilleures salles de Paris",
            "Comment lire une voie efficacement",
            "L'échauffement parfait avant de grimper",
            "Récupération et prévention des blessures",
            "Alpinisme : mon ascension du Mont-Blanc",
        ]

        articles_created = 0
        for title in climbing_titles:
            if not Article.objects.filter(title=title).exists():
                article = Article.objects.create(
                    title=title,
                    excerpt=fake.paragraph(nb_sentences=2),
                    content=self._generate_article_content(),
                    image_url=f'https://picsum.photos/seed/{fake.uuid4()}/1200/600',
                    author=random.choice(authors),
                    category=random.choice(categories),
                    status=random.choices(['draft', 'published'], weights=[0.2, 0.8])[0],
                    published_at=timezone.now() - timezone.timedelta(days=random.randint(0, 60))
                )
                article.tags.set(random.sample(tags, k=random.randint(2, 5)))
                articles_created += 1
        self.stdout.write(f'  Created {articles_created} articles')

    def _generate_article_content(self):
        paragraphs = [fake.paragraph(nb_sentences=random.randint(4, 8)) for _ in range(random.randint(4, 7))]
        return '\n\n'.join(paragraphs)

    def create_comments(self):
        articles = Article.objects.filter(status='published')
        users = list(User.objects.all())

        comments_created = 0
        for article in articles:
            # Create 2-6 root comments per article
            num_comments = random.randint(2, 6)
            for _ in range(num_comments):
                root_comment = Comment.objects.create(
                    article=article,
                    author=random.choice(users),
                    content=fake.paragraph(nb_sentences=random.randint(1, 3)),
                )
                comments_created += 1

                # 50% chance of having 1-2 replies
                if random.random() > 0.5:
                    num_replies = random.randint(1, 2)
                    for _ in range(num_replies):
                        Comment.objects.create(
                            article=article,
                            author=random.choice(users),
                            content=fake.paragraph(nb_sentences=random.randint(1, 2)),
                            parent=root_comment,
                        )
                        comments_created += 1

        self.stdout.write(f'  Created {comments_created} comments')
