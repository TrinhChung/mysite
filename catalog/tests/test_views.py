import uuid
from django.test import TestCase
from catalog.models import Author, Genre, Book, BookInstance
from django.contrib.auth.models import Permission
from catalog.factory import (
    UserFactory,
    AuthorFactory,
    GenreFactory,
    BookFactory,
    BookInstanceFactory,
)
import datetime
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User
from django.utils import timezone


class HomeViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = AuthorFactory()
        book = BookFactory.create(genres=([GenreFactory()]), author=author)

    def test_redirect(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "base_generic.html")


class BookListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_books = 13

        for book_id in range(number_of_books):
            BookFactory()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/catalog/books/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/book_list.html")

    def test_pagination_is_ten(self):
        response = self.client.get(reverse("books"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["book_list"]), 10)

    def test_lists_all_authors(self):
        response = self.client.get(reverse("books") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["book_list"]), 3)


class AuthorListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        number_of_authors = 13

        for author_id in range(number_of_authors):
            AuthorFactory()

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get("/catalog/authors/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/author_list.html")

    def test_pagination_is_ten(self):
        response = self.client.get(reverse("authors"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["author_list"]), 10)

    def test_lists_all_authors(self):
        response = self.client.get(reverse("authors") + "?page=2")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("is_paginated" in response.context)
        self.assertTrue(response.context["is_paginated"] == True)
        self.assertEqual(len(response.context["author_list"]), 3)


class BookViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.book = BookFactory(genres=([GenreFactory(), GenreFactory()]))
        cls.bookInstance = BookInstanceFactory(book=cls.book, borrower=cls.user)

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(reverse("book-detail", kwargs={"pk": self.book.pk}))
        print(response)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(reverse("book-detail", kwargs={"pk": self.book.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/book_detail.html")

    def test_copies_is_only(self):
        response = self.client.get(reverse("book-detail", kwargs={"pk": self.book.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["book_instance"]), 1)


class AuthorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = AuthorFactory()
        cls.book = BookFactory(
            genres=([GenreFactory(), GenreFactory()]), author=cls.author
        )

    def test_view_url_exists_at_desired_location(self):
        response = self.client.get(
            reverse("author-detail", kwargs={"pk": self.author.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        response = self.client.get(
            reverse("author-detail", kwargs={"pk": self.author.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/author_detail.html")

    def test_book_is_only(self):
        response = self.client.get(
            reverse("author-detail", kwargs={"pk": self.author.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["books"]), 1)


class LoanedBookInstancesByUserListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user1 = UserFactory(username="user11")
        author = AuthorFactory()
        book = BookFactory.create(
            genres=([GenreFactory(), GenreFactory()]), author=author
        )
        number_of_book_copies = 15
        for book_copy in range(number_of_book_copies):
            return_date = timezone.localtime() + datetime.timedelta(days=book_copy % 5)
            BookInstanceFactory(
                book=book, borrower=user1, due_back=return_date, status="m"
            )

        cls.client = Client()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("my-borrowed"))
        self.assertRedirects(response, "/accounts/login/?next=/catalog/mybooks/")

    def test_logged_in_uses_correct_template(self):
        self.client.login(username="user11", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("my-borrowed"))
        self.assertEqual(str(response.context["user"]), "user11")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
            response, "catalog/bookinstance_list_borrowed_user.html"
        )

    def test_only_borrowed_books_in_list(self):
        self.client.login(username="user11", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("my-borrowed"))

        self.assertEqual(str(response.context["user"]), "user11")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("bookinstance_list" in response.context)
        self.assertEqual(len(response.context["bookinstance_list"]), 0)

        books = BookInstance.objects.all()[:10]

        for book in books:
            BookInstance.objects.filter(id=book.id).update(status="o")

        response = self.client.get(reverse("my-borrowed"))
        self.assertEqual(str(response.context["user"]), "user11")
        self.assertEqual(response.status_code, 200)
        self.assertTrue("bookinstance_list" in response.context)

        for bookitem in response.context["bookinstance_list"]:
            self.assertEqual(response.context["user"], bookitem.borrower)
            self.assertEqual(bookitem.status, "o")

    def test_pages_ordered_by_due_date(self):
        for book in BookInstance.objects.all():
            book.status = "o"
            book.save()

        self.client.login(username="user11", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("my-borrowed"))
        self.assertEqual(str(response.context["user"]), "user11")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["bookinstance_list"]), 10)

        last_date = 0
        for book in response.context["bookinstance_list"]:
            if last_date == 0:
                last_date = book.due_back
            else:
                self.assertTrue(last_date <= book.due_back)
                last_date = book.due_back


class RenewBookInstancesViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        user1 = UserFactory(username="user1")
        user2 = UserFactory(username="user2")

        user1.save()
        user2.save()

        permission = Permission.objects.get(name="Can mark returned book")
        prm2 = Permission.objects.get(name="Get all book on loan")
        user2.user_permissions.add(permission, prm2)
        user2.save()

        # Create a book
        author = AuthorFactory()
        book = BookFactory.create(genres=([GenreFactory()]), author=author)

        # Create a BookInstance object for user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        cls.bookinstance1 = BookInstanceFactory(
            book=book,
            due_back=return_date,
            borrower=user1,
            status="o",
        )

        # Create a BookInstance object for user2
        cls.bookinstance2 = BookInstanceFactory(
            book=book,
            due_back=return_date,
            borrower=user2,
            status="o",
        )

        cls.client = Client()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.bookinstance1.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(username="user1", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.bookinstance1.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_borrowed_book(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.bookinstance2.id})
        )
        self.assertEqual(response.status_code, 200)

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        test_uid = uuid.uuid4()
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": test_uid})
        )
        self.assertEqual(response.status_code, 404)

    def test_uses_correct_template(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.bookinstance1.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "catalog/book_renew_librarian.html")

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("renew-book-librarian", kwargs={"pk": self.bookinstance1.pk})
        )
        self.assertEqual(response.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(
            response.context["form"].initial["due_back"], date_3_weeks_in_future
        )

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        response = self.client.post(
            reverse(
                "renew-book-librarian",
                kwargs={
                    "pk": self.bookinstance1.pk,
                },
            ),
            {"due_back": valid_date_in_future},
        )
        self.assertRedirects(response, reverse("bookinst-manage"))

    def test_form_invalid_renewal_date_past(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        response = self.client.post(
            reverse("renew-book-librarian", kwargs={"pk": self.bookinstance1.pk}),
            {"due_back": date_in_past},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, "form", "due_back", "Invalid date - renewal in past"
        )

    def test_form_invalid_renewal_date_future(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        response = self.client.post(
            reverse("renew-book-librarian", kwargs={"pk": self.bookinstance1.pk}),
            {"due_back": invalid_date_in_future},
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response,
            "form",
            "due_back",
            "Invalid date - renewal more than 4 weeks ahead",
        )


class CreateAuthorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        user1 = UserFactory(username="user1")
        user2 = UserFactory(username="user2")

        user1.save()
        user2.save()

        permission = Permission.objects.get(codename="add_author")
        user1.user_permissions.add(permission)
        user1.save()

        cls.client = Client()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse("author-create"))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("author-create"))
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_add_author(self):
        self.client.login(username="user1", password="1X<ISRUkw+tuK")
        response = self.client.get(reverse("author-create"))
        self.assertEqual(response.status_code, 200)


class UpdateAuthorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        user1 = UserFactory(username="user1")
        user2 = UserFactory(username="user2")

        user1.save()
        user2.save()

        permission = Permission.objects.get(codename="change_author")
        user1.user_permissions.add(permission)
        user1.save()

        cls.author = AuthorFactory()

        cls.client = Client()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("author-update", kwargs={"pk": self.author.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("author-update", kwargs={"pk": self.author.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_add_author(self):
        self.client.login(username="user1", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("author-update", kwargs={"pk": self.author.id})
        )
        self.assertEqual(response.status_code, 200)


class DeleteAuthorViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Create a user
        user1 = UserFactory(username="user1")
        user2 = UserFactory(username="user2")

        user1.save()
        user2.save()

        permission = Permission.objects.get(codename="delete_author")
        user1.user_permissions.add(permission)
        user1.save()

        cls.author = AuthorFactory()

        cls.client = Client()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(
            reverse("author-delete", kwargs={"pk": self.author.id})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url.startswith("/accounts/login/"))

    def test_forbidden_if_logged_in_but_not_correct_permission(self):
        self.client.login(username="user2", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("author-delete", kwargs={"pk": self.author.id})
        )
        self.assertEqual(response.status_code, 403)

    def test_logged_in_with_permission_add_author(self):
        self.client.login(username="user1", password="1X<ISRUkw+tuK")
        response = self.client.get(
            reverse("author-delete", kwargs={"pk": self.author.id})
        )
        self.assertEqual(response.status_code, 200)
