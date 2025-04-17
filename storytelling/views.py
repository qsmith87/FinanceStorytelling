from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from scripts.get10k import fetch_and_process_10k

def index(request):
    return render(request, 'story/index.html')

def analyze(request):
    if request.method == 'POST':
        ticker = request.POST.get('ticker')
        data = fetch_and_process_10k(ticker)
        return render(request, 'story/results.html', {'data': data})
    return render(request, 'story/index.html')
