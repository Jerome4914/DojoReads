from django.db import models
from datetime import datetime
import bcrypt, re
# Create your models here.

class UserManager(models.Manager):
    def registration_validator(self, postData):
        errors = {}
        EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        # PASSWORD_REGEX = re.compile(r'^(?=.*?[A-Z][a-zA-Z!"#\$%&\(\)\*\+,-\.\/:;<=>\?@[\]\^_\{\}~]]$')
        if len(postData['first_name']) < 2:
            errors['first_name'] = "Name must be more than 2 characters"
        if len(postData['alias']) < 2:
            errors['alias'] = "Alias Name must be more than 2 characters"
        if len(postData['email']) == 0:
            errors['register_email'] = "You must enter an email"
        if not EMAIL_REGEX.match(postData['email']):
            errors['register_email'] = "Invalid email address"
        current_users = User.objects.filter(email=postData['email'])
        if len(current_users) > 0:
            errors['register_email'] = "That email already exists"
        if len(postData['password']) < 8:
            errors['register_password'] = "Password should be at least 8 characters"
        if (postData['password']) != (postData['confirm_password']):
            errors['register_password'] = "Passwords do not match"
        # if not PASSWORD_REGEX.match(postData['password']):
        #     errors['register_password'] = "Password must contain a special character and 1 uppercase letter"  
        return errors

    def login_validator(self, postData):
        errors = {}
        current_users = User.objects.filter(email=postData['email'])

        if len(current_users) != 1:
            errors['login_email'] = "User does not exist"
        elif bcrypt.checkpw(postData['password'].encode(), current_users[0]. password.encode()) != True:
            errors['login_password'] = "Email or Password do not match"
        if len(postData['email']) == 0:
            errors['login_email'] = "Email must be entered"
        if len(postData['password']) < 8:
            errors['login_password'] = "Password should be at least 8 characters"
        return errors

class BookManager(models.Manager):
    def book_validator(self, postData):
        errors = {}
        if len(postData['title']) < 2:
            errors['title'] = "Title should be at least 2 characters"
        return errors

class AuthorManager(models.Manager):
    def author_validator(self, postData):
        errors = {}
        if len(postData['author_name']) < 2:
            errors['author_name'] = "Author Name should be at least 2 characters"
        author_in_db = Author.objects.filter(name=postData['author_name'])
        if len(author_in_db) >= 1:
            errors['author_name'] = "Author already exists"
        return errors

class ReviewManager(models.Manager):
    def review_validator(self, postData):
        errors = {}
        if len(postData['content']) < 10:
            errors["content"] = "Review should be at least 10 characters"
        return errors

class User(models.Model):
    first_name = models.CharField(max_length=50)
    alias = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    #"user_reviews"

class Book(models.Model):
    title = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = BookManager()
    #"authors"
    #"book_reviews"

class Author(models.Model):
    name = models.CharField(max_length=50)
    books = models.ManyToManyField(Book, related_name="authors")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = AuthorManager()

class Review(models.Model):
    content = models.TextField()
    rating = models.IntegerField()
    user_review = models.ForeignKey(User, related_name="user_reviews", on_delete=models.CASCADE)
    book_reviewed = models.ForeignKey(Book, related_name="book_reviews", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ReviewManager()
