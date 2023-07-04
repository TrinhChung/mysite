import factory
from factory.django import DjangoModelFactory
from catalog.constant import LOAN_STATUS
from catalog.models import Book, Author, BookInstance, Genre
from django.contrib.auth.models import User
import random, string
from datetime import datetime


def randomWord(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence("user{}".format)
    email = factory.Sequence("user{}@company.com".format)
    password = factory.PostGenerationMethodCall("set_password", "1X<ISRUkw+tuK")
    is_superuser = False
    is_staff = True
    is_active = True


class AuthorFactory(DjangoModelFactory):
    class Meta:
        model = Author

    first_name = randomWord(5)
    last_name = randomWord(8)


class GenreFactory(DjangoModelFactory):
    class Meta:
        model = Genre

    name = randomWord(10)


class BookFactory(DjangoModelFactory):
    class Meta:
        model = Book

    title = randomWord(10)
    summary = randomWord(10)
    isbn = factory.Sequence("123456{}".format)

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create or not extracted:
            return

        for genre_in in extracted:
            self.genre.add(genre_in)


class BookInstanceFactory(DjangoModelFactory):
    class Meta:
        model = BookInstance

    imprint = randomWord(10)
    due_back = datetime.strptime("2023-01-01", "%Y-%m-%d").date()
    # borrower = factory.RelatedFactory(UserFactory, is_superuser=True)
    status = "o"
