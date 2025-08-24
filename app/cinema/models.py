from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.conf import settings




class Roles(models.TextChoices):
    Author = "AUTHOR"
    SPECTATOR = "SPECTATOR"
    
class Gender(models.IntegerChoices):
    NOT_SPECIFIED = 0,
    FEMALE = 1,
    MALE = 2, 
    NON_BINARY = 3,

    
class User(AbstractUser):
    email = models.EmailField(unique=True)
    date_of_birth = models.DateField(null=True, blank=True)
    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.SPECTATOR,
    )
    created_at = models.DateTimeField(auto_now_add=True, blank=False, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    password = models.CharField(
        max_length=200,
        validators=[
            RegexValidator(
                r"^(?=.*\d).{8,}$",
                "Your password must contain at least eight characters, one number and one letter.",
            )
        ],
        error_messages={
            "required": "Please enter your password",
            "max_length": "Your password cannot exceed 200 characters.",
        },
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def save(self, *args, **kwargs):
        if self.email:
            self.email = self.email.lower().strip()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return (f"{self.first_name} {self.last_name}".strip() or self.username)
    
class Author(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="author", primary_key=True)
    popularity = models.FloatField(default=0.0)
    tmdb_id = models.PositiveIntegerField(blank=True, null=True, unique=True)
    website = models.URLField(blank=True, null=True)
    death_date = models.DateField(null=True, blank=True)
    gender = models.IntegerField(
        choices=Gender.choices,
        default=Gender.NOT_SPECIFIED,
    )
    department = models.CharField(max_length=200,blank=True,null=True)

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"
    
class Spectator(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="spectator", primary_key=True)
    bio = models.TextField(
        blank=True, 
        null=True, 
    )
    favorite_films = models.ManyToManyField(
        "cinema.Film", related_name="favorite_films", blank=True
    )
    favorite_authors = models.ManyToManyField("cinema.Author", related_name="favorite_authors", blank=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"


    
class FilmStatus(models.TextChoices):
    DRAFT = "DRAFT"
    RELEASED = "RELEASED"
    ARCHIVED = "ARCHIVED"
    
class Film(models.Model):    
    title = models.CharField(max_length=200)
    description = models.TextField(max_length=2000, blank=True)
    release_date = models.DateField(null=True, blank=True)
    # evaluation = models.FloatField(null=True,blank=True)
    statut = models.CharField(
        max_length=20,
        choices=FilmStatus.choices,
        default=FilmStatus.RELEASED,
    )
    authors = models.ManyToManyField(
        Author,
        related_name='authors_films',
        blank=True
    )
    
    tmdb_id = models.IntegerField(
        null=True, 
        blank=True, 
        unique=True,
    )
    budget = models.BigIntegerField(
        null=True, 
        blank=True,
    )
    revenue = models.BigIntegerField(
        null=True, 
        blank=True,
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    def __str__(self):
        return self.title
    
class FilmRating(models.Model):
    spectator = models.ForeignKey(
        Spectator,
        on_delete=models.CASCADE,
        related_name='ratings_film',
    )
    film = models.ForeignKey(
        Film,
        on_delete=models.CASCADE,
        related_name='ratings',
    )
    note = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )

    def __str__(self):
        return f"{self.spectator} - {self.film} ({self.note})"


class AuthorRating(models.Model):
    spectator = models.ForeignKey(
        Spectator,
        on_delete=models.CASCADE,
        
    )
    author = models.ForeignKey(
        Author,
        on_delete=models.CASCADE,
    )
    note = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
    )
    def __str__(self):
        return f"{self.spectator} - {self.film} ({self.note})"