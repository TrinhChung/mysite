from django.utils.translation import gettext
from django.http import Http404
from catalog.models import Book, Author, BookInstance
from django.views import generic
import datetime
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from catalog.forms import RenewBookModelForm
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

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


class LoanedBooksByUserListView(LoginRequiredMixin, generic.ListView):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    template_name = "catalog/bookinstance_list_borrowed_user.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.filter(borrower=self.request.user)
            .filter(status__exact="o")
            .order_by("due_back")
        )


class LoanedBooksManageListView(
    LoginRequiredMixin, PermissionRequiredMixin, generic.ListView
):
    """Generic class-based view listing books on loan to current user."""

    model = BookInstance
    permission_required = "catalog.view_list_on_loan"
    template_name = "catalog/bookinstance_manage.html"
    paginate_by = 10

    def get_queryset(self):
        return (
            BookInstance.objects.all()
            .filter(status__exact="o")
            .order_by("-due_back")
            .select_related("borrower")
        )


@login_required
@permission_required("catalog.can_mark_returned", raise_exception=True)
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == "POST":
        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookModelForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data["due_back"]
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse("bookinst-manage"))

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookModelForm(initial={"due_back": proposed_renewal_date})

    context = {
        "form": form,
        "book_instance": book_instance,
    }

    return render(request, "catalog/book_renew_librarian.html", context)


class AuthorCreate(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Author
    permission_required = "catalog.create_author"
    fields = ["first_name", "last_name", "date_of_birth", "date_of_death"]
    initial = {"date_of_death": "11/06/2020"}


class AuthorUpdate(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Author
    permission_required = "catalog.change_author"

    fields = (
        "__all__"  # Not recommended (potential security issue if more fields added)
    )


class AuthorDelete(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    model = Author
    permission_required = "catalog.delete_author"
    success_url = reverse_lazy("authors")
