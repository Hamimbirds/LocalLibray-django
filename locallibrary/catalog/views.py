from django.shortcuts import render
#import generic class
from django.views import generic

from django.shortcuts import get_object_or_404

# Create your views here.
from catalog.models import Book, Author, BookInstance, Genre

def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_books = Book.objects.all().count()
    num_instances = BookInstance.objects.all().count()

    # Available books (status = 'a')
    num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    num_authors = Author.objects.count()  # The 'all()' is implied by default.

    # Number of visits to this view, as counted in the session variable.
    num_visits = request.session.get('num_visits', 0)
    request.session['num_visits'] = num_visits + 1

    context = {
        'num_books': num_books,
        'num_instances': num_instances,
        'num_instances_available': num_instances_available,
        'num_authors': num_authors,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)


class BookListView(generic.ListView):
    model = Book
    paginate_by = 1

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get the context
        context = super(BookListView, self).get_context_data(**kwargs)
        # Create any data and add it to the context
        context['some_data'] = 'This is just some data'
        return context


class BookDetailView(generic.DetailView):
    model = Book


def book_detail_view(request, primary_key):
    book = get_object_or_404(Book, pk=primary_key)
    return render(request, 'catalog/book_detail.html', context={'book': book})


class AuthorListView(generic.ListView):
    """Generic class-based list view for a list of authors."""
    model = Author
    paginate_by = 1


class AuthorDetailView(generic.DetailView):
        model = Author


def book_detail_view(request, primary_key):
        author = get_object_or_404(author, pk=primary_key)
        return render(request, 'catalog/author_detail.html', context={'author': author})

from django.contrib.auth.mixins import LoginRequiredMixin

class LoanedBooksByUserListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing books on loan to current user."""
    model = BookInstance
    template_name ='catalog/bookinstance_list_borrowed_user.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(borrower=self.request.user).filter(status__exact='o').order_by('due_back')
# Added as part of challenge!
from django.contrib.auth.mixins import PermissionRequiredMixin


class LoanedBooksAllListView(PermissionRequiredMixin, generic.ListView):
    """Generic class-based view listing all books on loan. Only visible to users with can_mark_returned permission."""
    model = BookInstance
    permission_required = 'catalog.can_mark_returned'
    template_name = 'catalog/bookinstance_list_borrowed_all.html'
    paginate_by = 10

    def get_queryset(self):
        return BookInstance.objects.filter(status__exact='o').order_by('due_back')


import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.urls import reverse

from catalog.forms import RenewBookForm

@permission_required('catalog.can_mark_returned')
def renew_book_librarian(request, pk):
    book_instance = get_object_or_404(BookInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = RenewBookForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            book_instance.due_back = form.cleaned_data['renewal_date']
            book_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('all-borrowed') )

    # If this is a GET (or any other method) create the default form.
    else:
        proposed_renewal_date = datetime.date.today() + datetime.timedelta(weeks=3)
        form = RenewBookForm(initial={'renewal_date': proposed_renewal_date})

    context = {
        'form': form,
        'book_instance': book_instance,
    }

    return render(request, 'catalog/book_renew_librarian.html', context)



from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy



class AuthorCreate(CreateView):
    model = Author
    fields = '__all__'
    initial = {'date_of_death': '05/01/2018'}

class AuthorUpdate(UpdateView):
    model = Author
    fields = ['first_name', 'last_name', 'date_of_birth', 'date_of_death']

class AuthorDelete(DeleteView):
    model = Author
    success_url = reverse_lazy('authors')


class BookCreate(CreateView):
    model = Book
    fields = '__all__'


class BookUpdate(UpdateView):
    model = Book
    fields = '__all__'

class BookDelete(DeleteView):
    model = Book
    success_url = reverse_lazy('books')
