from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Book, Author, Review
import bcrypt

# Create your views here.
def index(request):
    return render(request, "index.html")

def create_user(request):
    if request.method == "POST":
        errors = User.objects.registration_validator(request.POST)

        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return redirect('/')

        hash_pw = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt()).decode()
        new_user = User.objects.create(
            first_name = request.POST['first_name'],
            alias = request.POST['alias'],
            email = request.POST['email'],
            password = hash_pw
        )
        request.session['current_users'] = new_user.id
        return redirect('/user/dashboard')
    return redirect('/')

def dashboard(request):

    context = {
        'current_users': User.objects.get(id=request.session['current_users']),
        'all_books': Book.objects.all(),
        'recent_reviews': Review.objects.order_by('created_at').reverse()[0:3]
    }
    return render(request, 'dashboard.html', context)

def login(request):
    if request.method == "POST":
        errors = User.objects.login_validator(request.POST)

        if len(errors) > 0:
            for key, value in errors.items():
                messages.error(request, value, extra_tags=key)
            return redirect('/')
        this_user = User.objects.filter(email=request.POST['email'])
        request.session['current_users'] = this_user[0].id
        return redirect('/user/dashboard')

    return redirect('/')

def create_book(request):

    #This is so that book_validator and review_validator can run simeltaniously 
    if request.method == "POST":
        
        book_errors = Book.objects.book_validator(request.POST)
        review_errors = Review.objects.review_validator(request.POST)
        errors = list(book_errors.values())+list(review_errors.values())

        #Only running this if the user is creating an author
        if request.POST['author_dropdown'] == "-1":
            if request.POST['author_name'] == "":
                messages.error(request, "Please either choose an author from the dropdown or create a new one")
            else:
                author_errors = Author.objects.author_validator(request.POST)
                #dictionary of errors=list(book_errors.values())+list(review_errors.values()) listed above
                errors += list(author_errors.values())
        
        if len(errors) > 0:
                    
            for error in errors:
                messages.error(request, error)    
            return redirect('/book/book_form')
        
        if request.POST['author_dropdown'] == "-1":
            author = Author.objects.create(name=request.POST['author_name'])
        else:
            author = Author.objects.get(id=request.POST['author_dropdown'])
            
        book = Book.objects.create(title=request.POST['title'])
        user = User.objects.get(id=request.session['current_users'])
        review = Review.objects.create(content=request.POST['content'], rating=int(request.POST['rating']), user_review=user, book_reviewed=book)
        book.authors.add(author)
        return redirect(f'/book/{book.id}')

        # print("No errors!")

    return redirect('/book/book_form')

def book_form(request):
    if 'current_users' not in request.session:
        return redirect('/')

    context = {
        'authors': Author.objects.all()
    }
    return render(request, 'add_book.html', context) 

def show_book(request, book_id):
    context = {
        'book': Book.objects.get(id=book_id)
    }
    return render(request, "one_book.html", context)

def logout_user(request):

    request.session.clear()
    return redirect('/')

def add_review(request):
    if request.method == "POST":
    
        book = Book.objects.get(id=request.POST['book_reviewed'])
        errors = Review.objects.review_validator(request.POST)

        if errors:
            for key, value in errors.items():
                messages.error(request, value)
            return redirect(f'/book/{book.id}')

        user = User.objects.get(id=request.session['current_users'])
        review = Review.objects.create(content=request.POST['content'], rating=int(request.POST['rating']), user_review=user, book_reviewed=book)
    return redirect(f'/book/{book.id}')

def user_page(request, user_id):
    user = User.objects.get(id=user_id)

    context = {
        "one_user": user
    }
    return render(request, 'user_page.html', context)

def delete_review(request, review_id):
    if 'current_users' not in request.session:
        messages.error(request, "Please register or log in first!")
        return redirect('/')
    review = Review.objects.get(id=review_id)
    review.delete()
    return redirect(f'/book/{review.book_reviewed.id}')