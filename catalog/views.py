from django.utils.translation import gettext
from django.http import Http404
from django.shortcuts import render
from catalog.models import Book, Author, BookInstance, Genre
from django.views import generic
import datetime

# Create your views here.


def index(request):
    """View function for home page of site."""
    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()
    num_instances_available = BookInstance.objects.filter(status__exact="a").count()
    num_authors = Author.objects.count()
    num_visits = request.session.get("num_visits", 1)
    request.session["num_visits"] = num_visits + 1
    age_cookie = request.session.get_session_cookie_age()
    context = {
        "num_books": num_books,
        "num_instances": num_instances,
        "num_instances_available": num_instances_available,
        "num_authors": num_authors,
        "num_visits": num_visits,
        "age_cookie": datetime.timedelta(seconds=age_cookie),
    }

    return render(request, "index.html", context=context)


class BookListView(generic.ListView):
    model = Book
    # your own name for the list as a template variable
    paginate_by = 2

    def get_queryset(self):
        return Book.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        return context


class BookDetailView(generic.DetailView):
    model = Book

    def book_detail_view(request, primary_key):
        try:
            book = Book.objects.get(pk=primary_key)
        except Book.DoesNotExist:
            raise Http404(gettext("Book does not exist"))

        return render(request, "catalog/book_detail.html", context={"book": book})

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookDetailView, self).get_context_data(**kwargs)
        context["book_instance"] = context["book"].bookinstance_set.order_by(
            "-due_back"
        )
        return context


class AuthorListView(generic.ListView):
    model = Author
    # your own name for the list as a template variable
    paginate_by = 2

    def get_queryset(self):
        return Author.objects.all()

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(AuthorListView, self).get_context_data(**kwargs)
        # # Create any data and add it to the context
        # context["some_data"] = "This is just some data"
        return context


class AuthorDetailView(generic.DetailView):
    model = Author

    def author_detail_view(request, primary_key):
        try:
            author = Author.objects.get(pk=primary_key).select_related("book")
        except Author.DoesNotExist:
            raise Http404(gettext("Author does not exist"))

        return render(request, "author/author_detail.html", context={"author": author})

    def get_context_data(self, **kwargs):
        context = super(AuthorDetailView, self).get_context_data(**kwargs)
        context["books"] = context["author"].book_set.all()
        return context
