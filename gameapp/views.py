from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
import requests
from bs4 import BeautifulSoup
from .models import Quotes
from random import choice
from .forms import AnswerValid

BASE_URL = "http://quotes.toscrape.com"
remaining_guesses = 4

# Create your views here.

def home(request):
    try:
        authors = Quotes.objects.values('author').distinct()
        data = {'authors':authors}
        return render(request,'gameapp/home.html',context = data)
    except:
        print('Some error')
    
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
    
    scraped = 'Web Scraping has been completed with latest updates. U can now play game'
    data = {
        'scraped':scraped,
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
    link = request.session['link']
    author_born_date = request.session['born']
    author_born_location = request.session['location']

    global remaining_guesses
    answer = ''

    if remaining_guesses == 0 or remaining_guesses == -1:
        remaining_guesses = 4

    while answer != author and remaining_guesses >= 0:
        if request.method == 'POST':
            if request.is_ajax():
                form = AnswerValid(request.POST)
                if form.is_valid():
                    answer = form.cleaned_data.get('user_answer')
                    remaining_guesses -= 1
                    print(remaining_guesses)

                    if answer == author:
                        ans = 'Correct Answer'
                        rem = 'Ur guess was right.. Hats off!'
                        hint = 'Be happy.. ur answer was right... Click on Play again for try again'
                        remaining_guesses=4
                        return JsonResponse({'data':ans,'rem':rem,'hint':hint})

                    elif remaining_guesses == 3 and answer.lower() != author.lower():
                        ans = 'Let me give u one hint..'
                        print(author,author_born_date,author_born_location)
                        hint = f'That person was born on {author_born_date} {author_born_location}'
                        print(f'remaining guesses:{remaining_guesses}')
                        return JsonResponse({'data':ans,'rem':remaining_guesses,'hint':hint})

                    elif remaining_guesses == 2 and answer.lower() != author.lower():
                        ans = 'One hint wasted.. No worries. One more hint'
                        hint = f'Name starts with {author[0]}'
                        print(f'remaining guesses:{remaining_guesses}')
                        return JsonResponse({'data':ans,'rem':remaining_guesses,'hint':hint})

                    elif remaining_guesses == 1 and answer.lower() != author.lower():
                        ans = 'Oh no this is the last hint. Answer or ur life is finished..'
                        last_name_initial = author.split(' ')[1][0]
                        hint = f'Name ends with {last_name_initial}'
                        print(f'remaining guesses:{remaining_guesses}')
                        return JsonResponse({'data':ans,'rem':remaining_guesses,'hint':hint})

                    elif remaining_guesses == 0 and answer.lower() != author.lower():
                        ans = f'U lost the game... The correct answer is {author}'
                        hint = 'Now no hint.. u lost the match.. click on Play Again if want to try once more' 
                        return JsonResponse({'data':ans,'rem':remaining_guesses,'hint':hint})
                else:
                    print(form.errors)
                    return JsonResponse({'error': True,'data':form.errors})
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


    



    
