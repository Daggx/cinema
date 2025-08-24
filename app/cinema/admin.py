from django.contrib import admin
from django.contrib.auth.admin import UserAdmin 
from django.utils.html import format_html
from django.db.models import Count, Avg
from .models import User, Author, Spectator, Film, FilmRating, AuthorRating


############################# user ########################
@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = ('email', 'username', 'first_name', 'last_name', 'role', 'date_joined', 'is_active')
    list_filter = ('role', 'is_active', 'date_joined')
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('role', {
            'fields': ('date_of_birth', 'role')
        }),
    )
###########################################################
    

# Inline classes 
class FilmInline(admin.TabularInline):
    model = Film.authors.through
    extra = 1


class FilmRatingInline(admin.TabularInline):
    model = FilmRating
    extra = 0

class AuthorRatingInline(admin.TabularInline):
    model = AuthorRating
    extra = 0


############################# Author ########################

# add filter authors with more than 1 movie
class HasFilmsFilter(admin.SimpleListFilter):
    title = 'Has films'  # display name in admin
    parameter_name = 'has_films'

    def lookups(self, request, model_admin):
        return (
            ('yes', 'At least 1 film'),
            ('no', 'No films'),
        )

    def queryset(self, request, queryset):
        if self.value() == 'yes':
            return queryset.annotate(films_count=Count('authors_films')).filter(films_count__gte=1)
        if self.value() == 'no':
            return queryset.annotate(films_count=Count('authors_films')).filter(films_count=0)
        return queryset
    
@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('user_first_name','user_last_name', 'user_email', 'popularity', 'department', 'films_count')
    list_filter = ('gender', 'department', 'user__date_joined', HasFilmsFilter)
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'department')
    inlines = [FilmInline, AuthorRatingInline]
    

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            films_count=Count('authors_films', distinct=True)
        ).select_related('user')
    
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"
    user_email.admin_order_field = 'user__email'
    
    def user_first_name(self, obj):
        return obj.user.email
    user_first_name.short_description = "First Name"
    user_first_name.admin_order_field = 'user__first_name'
    
    def user_last_name(self, obj):
        return obj.user.email
    user_last_name.short_description = "Last Name"
    user_last_name.admin_order_field = 'user__last_name'
    
    def films_count(self, obj):
        return obj.films_count
    films_count.short_description = "NB films"
    films_count.admin_order_field = 'films_count'
    
############################################################

############################# Films ########################
@admin.register(Film)
class FilmAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'statut', 'average_rating', 'ratings_count', 'budget', 'revenue')
    list_filter = ('statut', 'release_date',)
    search_fields = ('title', 'description', 'authors__user__first_name', 'authors__user__last_name')
    inlines = [FilmRatingInline]
    

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        return queryset.annotate(
            avg_rating=Avg('ratings__note'),
            ratings_count=Count('ratings', distinct=True)
        ).prefetch_related('authors__user', 'ratings__spectator__user')
    
    def average_rating(self, obj):
        if hasattr(obj, 'avg_rating') and obj.avg_rating:
            return f"{obj.avg_rating:.1f}/5"
        return "No rating"

    def ratings_count(self, obj):
        return obj.ratings_count if hasattr(obj, 'ratings_count') else 0

##########################################################


############################# Spectator ########################
@admin.register(Spectator)
class SpectatorAdmin(admin.ModelAdmin):
    list_display = ('user_first_name','user_last_name', 'user_email', 'favorite_films_count', 'favorite_authors_count')
    search_fields = ('user__first_name', 'user__last_name', 'user__email', 'bio')
    filter_horizontal = ('favorite_films', 'favorite_authors')
    readonly_fields = ('favorite_films_list', 'favorite_authors_list', 'ratings_given')

    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user').prefetch_related(
            'favorite_films', 'favorite_authors', 'ratings_film', 'authorrating_set'
        )
    
    def get_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}".strip() or obj.user.username
    get_full_name.short_description = "Nom complet"
    get_full_name.admin_order_field = 'user__first_name'
    
    def user_email(self, obj):
        return obj.user.email
    user_email.short_description = "Email"
    user_email.admin_order_field = 'user__email'
    
    def user_first_name(self, obj):
        return obj.user.email
    user_first_name.short_description = "First Name"
    user_first_name.admin_order_field = 'user__first_name'
    
    def user_last_name(self, obj):
        return obj.user.email
    user_last_name.short_description = "Last Name"
    user_last_name.admin_order_field = 'user__last_name'
    
    def favorite_films_count(self, obj):
        return obj.favorite_films.count()
    favorite_films_count.short_description = "fav films"
    
    def favorite_authors_count(self, obj):
        return obj.favorite_authors.count()
    favorite_authors_count.short_description = "fav authors"
    
    def favorite_films_list(self, obj):
        films = obj.favorite_films.all()
        if films:
            film_links = []
            for film in films:
                url = f'/admin/cinema/film/{film.pk}/change/'
                film_links.append(f'<a href="{url}">{film.title}</a>')
            return format_html('<br>'.join(film_links))
        return "no fav films"
    favorite_films_list.short_description = "fav films"
    
    def favorite_authors_list(self, obj):
        authors = obj.favorite_authors.all()
        if authors:
            author_links = []
            for author in authors:
                url = f'/admin/cinema/author/{author.pk}/change/'
                name = f"{author.user.first_name} {author.user.last_name}".strip() or author.user.username
                author_links.append(f'<a href="{url}">{name}</a>')
            return format_html('<br>'.join(author_links))
        return "no fav authors"
    favorite_authors_list.short_description = "fav authors"
    
    def ratings_given(self, obj):
        film_ratings = obj.ratings_film.all()
        author_ratings = obj.authorrating_set.all()
        
        info = []
        if film_ratings:
            info.append("<strong>Films rating:</strong>")
            for rating in film_ratings:
                film_url = f'/admin/cinema/film/{rating.film.pk}/change/'
                info.append(f'<a href="{film_url}">{rating.film.title}</a>: {rating.note}/5')
        
        if author_ratings:
            info.append("<strong>Authors rating:</strong>")
            for rating in author_ratings:
                author_url = f'/admin/cinema/author/{rating.author.pk}/change/'
                author_name = f"{rating.author.user.first_name} {rating.author.user.last_name}".strip()
                info.append(f'<a href="{author_url}">{author_name}</a>: {rating.note}/10')
        
        return format_html('<br>'.join(info)) if info else "no rating"
    ratings_given.short_description = "Rating"

################################################################################################

@admin.register(FilmRating)
class FilmRatingAdmin(admin.ModelAdmin):
    list_display = ('spectator', 'film', 'note')
    list_filter = ('note', 'film__statut')
    search_fields = ('spectator__user__first_name', 'spectator__user__last_name', 'film__title')


@admin.register(AuthorRating)
class AuthorRatingAdmin(admin.ModelAdmin):
    list_display = ('spectator', 'author', 'note')
    list_filter = ('note',)
    search_fields = (
        'spectator__user__first_name', 
        'spectator__user__last_name',
        'author__user__first_name',
        'author__user__last_name'
    )
