from django.shortcuts import render, redirect, get_object_or_404
from .forms import RegistrationForm
from .models import *
from django.contrib.auth.decorators import login_required
from keras.models import load_model
from keras.preprocessing.sequence import pad_sequences
from .modelTraining.modelTraining import load_tokenizer
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from datetime import timedelta
from django.db.models import Count, Q
from django.utils import timezone
from django.core.mail import send_mail
from django.http import Http404
from django.http import HttpResponse
import random
import time

model = load_model('trained_imdb.h5')

def home(request):
    return render(request, 'home.html')

def login(request):
    if request.method == 'POST':
        redirect('home')
    return render(request, 'login.html')

def signup(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'registration/signup.html', {'form': form})

def faq(request):
    return render(request, 'faq.html')

def explore(request):
    genre = request.GET.get('genre')
    release_year = request.GET.get('release_year')
    selected_actors = request.GET.getlist('actors')
    streaming_platform = request.GET.get('streaming_platform')
    producer = request.GET.get('producers')
    films = Film.objects.all()
    if len(selected_actors) == 0:
        selected_actors.append('AllActors')
    if genre is not None:
        if 'AllGenres' not in genre:
            films = films.filter(genre=genre)
        if 'AllReleaseYears' not in release_year:
            films = films.filter(release_date__year=release_year)
        if 'AllActors' not in selected_actors:
            films = films.filter(actors__name__in=selected_actors).distinct()    
        if 'AllStreamingPlatforms' not in streaming_platform:
            films = films.filter(streaming_platform=streaming_platform)
        if 'AllProducers' not in producer:
            films = films.filter(producer__name=producer)
    

    return render(request, 'explore.html', {'films' : films})


def featuredToday(request):
    currentDate = timezone.now().date()
    start_of_week = timezone.now().date() - timezone.timedelta(days=timezone.now().weekday())
    end_of_week = start_of_week + timedelta(days=6)
    # Film.objects.all() face Select * pe tabela Film
    films = Film.objects.exclude(release_date__gt=currentDate)

    featured_films = random.sample(list(films), min(5, len(films)))

    fan_favorite_films = Film.objects.exclude(release_date__gt=currentDate).annotate(
        num_positive_reviews=Count('filmreview', filter=Q(filmreview__sentiment='positive')),
        num_negative_reviews=Count('filmreview', filter=Q(filmreview__sentiment='negative'))
    ).order_by('-num_positive_reviews', '-num_negative_reviews')[:2]

    # Algoritm care determină Top 5 movies of this week bazat pe sentimentul recenziei
    # Obține sentimentul recenziei din săptămâna curentă pentru fiecare film
    top_films_this_week = Film.objects.exclude(release_date__gt=currentDate).filter(
        filmreview__timestamp__gte=start_of_week,
        filmreview__timestamp__lte=end_of_week
        ).annotate(
        num_positive_reviews=Count('filmreview', filter=Q(filmreview__sentiment='positive')),
        num_negative_reviews=Count('filmreview', filter=Q(filmreview__sentiment='negative'))
    ).order_by('-num_positive_reviews', '-num_negative_reviews')[:5]

    # Film.object.filter face Select pe tabela Film. Selecteaza datele din tabela care au release Date-ul mai mare decat currentDate
    comingSoonFilms = Film.objects.filter(release_date__gt=currentDate)
    return render(request, 'featuredToday.html', {'films' : featured_films , 'comingSoonFilms' : comingSoonFilms, 'fanFavoriteFilms' : fan_favorite_films, 'topFilmsThisWeek' : top_films_this_week})

def film_detail(request, film_title):
    # get_object_or_404 face Select pe tabela Film. Selecteaza datele din tabela care au titlu egal cu cel din pagina
    film = get_object_or_404(Film, title=film_title)

    favorite_films = []
    if request.user.is_authenticated:
        favorite_films = list(request.user.extendeduser.favoriteMovies.values_list('title', flat=True))

    filmReviews = FilmReview.objects.filter(film=film)

    return render(request, 'film_detail.html', {'film': film, 'filmReviews' : filmReviews, 'favoriteFilms': favorite_films})

@login_required
def add_review(request, film_title):
    if request.method == 'POST':
        film = get_object_or_404(Film, title=film_title)
        num_reviews = FilmReview.objects.filter(film=film).count()
        current_user = request.user
        # luare rating din request-ul venit din pagina din frontend
        rating = request.POST.get('rating')
        review = request.POST.get('review')
        sentiment_prediction = predict_sentiment(review)
        score = film.score
        if score is None:
            score = 0
        score = 5
    
        if sentiment_prediction == "Positive":
            score += 0.05 * num_reviews
        elif sentiment_prediction == "Negative":
            score -= 0.05 * num_reviews
        score += 0.1 * int(rating)
    
        score = max(1, min(10, score))

        film.score = score
        film.save()

        # salvarea unui review in baza de date
        review_object = FilmReview.objects.create(
            user=current_user,
            film=film,
            rating=rating,
            text=review,
            sentiment=sentiment_prediction,
            timestamp=timezone.now()
        )        
        review_object.save()
    else:
        print("Request method is get")    
    return render(request, 'home.html')

# cautare film dupa titlu din search navbar
def searchMovies(request):
    query = request.GET.get('query', '').strip()
    if query:
        try:
            film = get_object_or_404(Film, title__iexact=query)
            filmReviews = FilmReview.objects.filter(film=film)
            return render(request, 'film_detail.html', {'film': film, 'filmReviews' : filmReviews})
        except Http404:
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    return redirect(request.META.get('HTTP_REFERER', 'home'))
    
@login_required
def userPage(request):
    if request.method =='POST':
        extended_user = ExtendedUser.objects.get(user=request.user)
        if 'avatar' in request.FILES:
            extended_user.avatar = request.FILES['avatar']
            extended_user.save()
            return redirect('user_page')
    else:
        extended_user = ExtendedUser.objects.get(user=request.user)
        return render(request, 'user_page.html', {'user' : request.user, 'extended_user' : extended_user})

def actor_detail(request, actor_name):
    actor = get_object_or_404(Actor, name=actor_name)
    return render(request, 'actor_detail.html', {'actor': actor})

@csrf_exempt
def add_to_favorites(request):
    if request.method == 'POST':
        film_title = request.POST.get('film_title')
        film = Film.objects.get(title=film_title)
        user = request.user
        if user.is_authenticated:
            try:
                film = Film.objects.get(title=film_title)
                user_profile = ExtendedUser.objects.get(user=user)
                user_profile.favoriteMovies.add(film)
                return JsonResponse({'message': 'Film added to favorites'}, status=200)
            except Film.DoesNotExist:
                return JsonResponse({'error': 'Film not found'}, status=404)
            except ExtendedUser.DoesNotExist:
                return JsonResponse({'error': 'User profile not found'}, status=404)
    else:
        print("Request method is get")    
        return render(request, 'home.html')    

@csrf_exempt
def remove_from_favorites(request):
    if request.method == 'POST':
        film_title = request.POST.get('film_title')
        user = request.user
        if user.is_authenticated:
            try:
                film = Film.objects.get(title=film_title)
                user_profile = ExtendedUser.objects.get(user=user)
                user_profile.favoriteMovies.remove(film)
                return JsonResponse({'message': 'Film removed from favorites'}, status=200)
            except Film.DoesNotExist:
                return JsonResponse({'error': 'Film not found'}, status=404)
            except ExtendedUser.DoesNotExist:
                return JsonResponse({'error': 'User profile not found'}, status=404)
    else:
        print("Request method is get")    
        return render(request, 'home.html')   

@login_required
def delete_account(request):
    if request.method == 'POST':
        request.user.delete()
        return redirect('home') 
    return render(request, 'delete_account.html') 

def film_help(request):
    all_producers = Producers.objects.all()
    genres = Film.objects.order_by().values_list('genre', flat=True).distinct()
    streaming_platforms = Film.objects.order_by().values_list('streaming_platform', flat=True).distinct()
    actors = Film.objects.order_by().values_list('actors__name', flat=True).distinct()
    release_years = Film.objects.order_by('release_date__year').values_list('release_date__year', flat=True).distinct()
    film_scores = Film.objects.order_by().values_list('score', flat=True).distinct()
    return render(request, 'film_help.html', {'all_producers' : all_producers, 'genres' : genres , 'streaming_platforms' : streaming_platforms , 'actors' : actors, 'release_years' : release_years, 'film_scores': film_scores}) 

def predict_sentiment(review):
    tokenizer = load_tokenizer('tokenizer.pickle')
    tokenized_review = tokenizer.texts_to_sequences([review])
    padded_review = pad_sequences(tokenized_review, padding='post', maxlen=500)
    sentiment_score = model.predict(padded_review)[0][0]
    print(sentiment_score)
    if sentiment_score >= 0.5:
        sentiment_label = "Positive"
    else:
        sentiment_label = "Negative"  
    return sentiment_label


def film_suggestions(request, search_term):
    films = Film.objects.filter(title__icontains=search_term).values('title')
    suggestions = [film['title'] for film in films]
    print(suggestions)
    return JsonResponse(suggestions, safe=False)

@login_required
def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if email == request.user.email:
            request.user.extendeduser.newsletter_subscribed = True
            request.user.extendeduser.save()
            send_mail(
                'Subscription Confirmation',
                'You are now subscribed to the MadaDB newsletter.',
                'madaaaiorda@gmail.com', 
                [email],
                fail_silently=False,
                )
            return redirect(request.META.get('HTTP_REFERER', 'home'))
        else:
            return JsonResponse({'error': 'Invalid subscription request'}, status=400)


@login_required
def unsubscribe_newsletter(request):
    if request.method == 'POST':
        request.user.extendeduser.newsletter_subscribed = False
        request.user.extendeduser.save()
        return redirect(request.META.get('HTTP_REFERER', 'home'))

def gdpr(request):
    return render(request, 'gdpr.html') 


def blog(request):
    return render(request, 'blog.html') 

def timeline(request):
    return render(request, 'timeline.html') 

def evolution(request):
    return render(request, 'evolution.html') 

def milestones(request):
    return render(request, 'milestones.html') 

def locations(request):
    return render(request, 'locations.html') 





