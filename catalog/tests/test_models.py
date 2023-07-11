from django.test import TestCase
from catalog.factory import (
    AuthorFactory,
    BookFactory,
    BookInstanceFactory,
    GenreFactory,
)
from catalog.models import Author, Genre, Book, BookInstance
import datetime
from django.contrib.auth.models import User


class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.author = AuthorFactory()

    def test_first_name_label(self):
        field_label = self.author._meta.get_field("first_name").verbose_name
        self.assertEqual(field_label, "first name")

    def test_date_of_death_label(self):
        field_label = self.author._meta.get_field("date_of_death").verbose_name
        self.assertEqual(field_label, "Died")

    def test_first_name_max_length(self):
        max_length = self.author._meta.get_field("first_name").max_length
        self.assertEqual(max_length, 100)

    def test_object_name_is_last_name_comma_first_name(self):
        expected_object_name = f"{self.author.last_name}, {self.author.first_name}"
        self.assertEqual(str(self.author), expected_object_name)

    def test_get_absolute_url(self):
        self.assertEqual(
            self.author.get_absolute_url(), "/catalog/author/%s" % self.author.id
        )


class GenreModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        cls.genre = GenreFactory()

    def test_name_label(self):
        field_label = self.genre._meta.get_field("name").verbose_name
        self.assertEqual(field_label, "name")

    def test_name_max_length(self):
        max_length = self.genre._meta.get_field("name").max_length
        self.assertEqual(max_length, 200)
        self.assertTrue(self.genre != None)

    def test_object_name(self):
        self.assertEqual(str(self.genre), self.genre.name)


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = AuthorFactory()
        cls.book = BookFactory.create(
            genres=(GenreFactory(), GenreFactory()), author=cls.author
        )

    def test_attribute(self):
        field_label_title = self.book._meta.get_field("title").verbose_name
        field_label_summary = self.book._meta.get_field("summary").verbose_name
        max_length_title = self.book._meta.get_field("title").max_length
        max_length_summary = self.book._meta.get_field("summary").max_length

        self.assertEqual(field_label_title, "title")
        self.assertEqual(field_label_summary, "summary")
        self.assertEqual(max_length_title, 200)
        self.assertEqual(max_length_summary, 1000)
        self.assertIsNotNone(self.book.title)

    def test_object_name(self):
        self.assertEqual(str(self.book), self.book.title)

    def on_delete_author(self):
        Author.objects.filter(id=self.book.author).delete()
        self.assertIsNone(self.book.author)

    def test_get_absolute_url(self):
        self.assertEqual(
            self.book.get_absolute_url(), "/catalog/book/%s" % self.book.id
        )


class BookInstanceModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.book = BookFactory.create(genres=(GenreFactory(), GenreFactory()))
        cls.bookInstance = BookInstanceFactory(book=cls.book)

    def test_attribute(self):
        field_label_imprint = self.bookInstance._meta.get_field("imprint").verbose_name
        max_length_status = self.bookInstance._meta.get_field("status").max_length
        max_length_imprint = self.bookInstance._meta.get_field("imprint").max_length

        self.assertEqual(field_label_imprint, "imprint")
        self.assertEqual(max_length_status, 1)
        self.assertEqual(max_length_imprint, 200)
        self.assertTrue(isinstance(self.bookInstance.due_back, datetime.date))
        self.assertTrue(self.bookInstance.is_overdue)

    def test_object_name(self):
        str_obj = f"{self.bookInstance.id} ({self.bookInstance.book.title})"
        self.assertEqual(str(self.bookInstance), str_obj)

    def on_delete_borrower(self):
        User.objects.filter(id=self.bookInstance.borrower.id).delete()
        self.assertIsNone(self.bookInstance.borrower)

    def on_delete_book(self):
        Genre.objects.filter(id=self.bookInstance.book.genre).delete()
        Author.objects.filter(id=self.bookInstance.book.author.id).delete()
        Book.objects.filter(id=self.bookInstance.book.id).delete()
        self.assertIsNone(BookInstance.objects.filter(self.bookInstance.id))
