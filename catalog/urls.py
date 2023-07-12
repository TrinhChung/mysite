from django.urls import include, path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("books/", views.BookListView.as_view(), name="books"),
    path("authors/", views.AuthorListView.as_view(), name="authors"),
    path("book/<int:pk>", views.BookDetailView.as_view(), name="book-detail"),
    path("author/<int:pk>", views.AuthorDetailView.as_view(), name="author-detail"),
    path("mybooks/", views.LoanedBooksByUserListView.as_view(), name="my-borrowed"),
    path(
        "bookinst-manage/",
        views.LoanedBooksManageListView.as_view(),
        name="bookinst-manage",
    ),
]
