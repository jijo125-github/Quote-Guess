from django.shortcuts import render,redirect
from django.http import JsonResponse, Http404
import requests
from bs4 import BeautifulSoup
from .models import Quotes
from random import choice
from .forms import AnswerValid

BASE_URL = "http://quotes.toscrape.com"
REMAINING_GUESSES = 4

# Create your views here.

def home(request):
    try:
        authors = Quotes.objects.values('author').distinct()
        data = {'authors':authors}
        return render(request,'gameapp/home.html',context = data)
    except:
        raise Http404


def scrape(request):
    url = '/page/1'
    while url:
        response = requests.get(f'{BASE_URL}{url}')
        print(f"Now Scraping {BASE_URL}{url}...")
        soup = BeautifulSoup(response.text,'html.parser')
        quotes = soup.find_all(class_='quote')

        for quote in quotes:
            name = quote.find('small').get_text()
            text = quote.find(class_='text').get_text()
            link = quote.find('a')['href']
            bioresponse = requests.get(f"{BASE_URL}{link}")
            print(f"Now Scraping {BASE_URL}{link}...")
            biosoup = BeautifulSoup(bioresponse.text,'html.parser')
            born = biosoup.find(class_="author-born-date").get_text()
            location = biosoup.find(class_="author-born-location").get_text()
            Quotes.objects.create(author = name, text = text, biolink = link, author_born = born, author_location = location)

        nextbtn = soup.find(class_='next')
        url = nextbtn.find('a')['href'] if nextbtn else None
    
    data = {
        'scraped' : True,
        'message' : 'Web Scraping has been completed with latest updates. U can now play game'
    }
    return render(request,'gameapp/home.html',context=data)   


def game(request):
    quotes = Quotes.objects.all()
    rand_quote_info = choice(quotes)
    request.session['quote'] = rand_quote_info.text
    request.session['author'] = rand_quote_info.author
    request.session['link'] = rand_quote_info.biolink
    request.session['born'] = rand_quote_info.author_born
    request.session['location'] = rand_quote_info.author_location
    return redirect('gameapp:actualgame')

def actualgame(request):
    quote = request.session['quote']
    author = request.session['author']
    # link = request.session['link']
    author_born_date = request.session['born']
    author_born_location = request.session['location']

    global REMAINING_GUESSES
    answer = ''

    if REMAINING_GUESSES == 0 or REMAINING_GUESSES == -1:
        REMAINING_GUESSES = 4

    while answer != author and REMAINING_GUESSES >= 0:
        if request.method == 'POST':
            if request.is_ajax():
                form = AnswerValid(request.POST)
                if form.is_valid():
                    answer = form.cleaned_data.get('user_answer')
                    REMAINING_GUESSES -= 1
                    print(REMAINING_GUESSES)

                    if answer == author:
                        REMAINING_GUESSES=4
                        data = {
                            'ans' : 'Correct Answer',
                            'rem' : 'Ur guess was right.. Hats off!',
                            'hint' : 'Be happy.. ur answer was right... Click on Play again for try again'
                        }
                        return JsonResponse(data)

                    elif REMAINING_GUESSES == 3 and answer.lower() != author.lower():
                        data = {
                            'ans' : 'Let me give u one hint..',
                            'rem' : REMAINING_GUESSES,
                            'hint' : f'That person was born on {author_born_date} {author_born_location}'
                        }
                        print(author,author_born_date,author_born_location)
                        print(f'remaining guesses:{REMAINING_GUESSES}')
                        return JsonResponse(data)

                    elif REMAINING_GUESSES == 2 and answer.lower() != author.lower():
                        data = {
                            'ans' : 'One hint wasted.. No worries. One more hint',
                            'rem' : REMAINING_GUESSES,
                            'hint' : f'Name starts with {author[0]}'
                        }
                        print(f'remaining guesses:{REMAINING_GUESSES}')
                        return JsonResponse(data)

                    elif REMAINING_GUESSES == 1 and answer.lower() != author.lower():
                        last_name_initial = author.split(' ')[1][0]
                        data = {
                            'ans' : 'Oh no this is the last hint. Answer or ur life is finished..',
                            'rem' : REMAINING_GUESSES,
                            'hint' : f'Name ends with {last_name_initial}'
                        }
                        print(f'remaining guesses:{REMAINING_GUESSES}')
                        return JsonResponse(data)

                    elif REMAINING_GUESSES == 0 and answer.lower() != author.lower():
                        data = {
                            'ans' : f'U lost the game... The correct answer is {author}',
                            'rem' : REMAINING_GUESSES,
                            'hint' : 'Now no hint.. u lost the match.. click on Play Again if want to try once more'
                        }
                        return JsonResponse(data)
                else:
                    print(form.errors)
                    data = {
                        'error' : True,
                        'data' : form.errors
                    }
                    return JsonResponse(data)
            else:
                error = {
                    'message': 'Error, must be an Ajax call.'
                }
                return JsonResponse(error,content_type='application/json')
        else:
            form = AnswerValid()
            data = {
                'quote':quote,
            }
            return render(request,'gameapp/game.html',context=data)


def quotesbyauthor(request,author):
    try:
        authorQS = Quotes.objects.filter(author = author)
        data = {
            'author':author,
            'quotes':authorQS
        }
        return render(request,'gameapp/authorquotes.html',context=data)

    except NameError:
        print('Enter valid author names')
