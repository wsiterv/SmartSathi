from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm
import json
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from .models import BookkeepingEntry
from django.db.models import Sum, Q
from decimal import Decimal
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import google.generativeai as genai
from gtts import gTTS
import io
import base64
from dotenv import load_dotenv
import os

load_dotenv()

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Account created! You can now log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
    return render(request, 'users/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def landing_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    return render(request, 'users/landing.html')

@login_required
def home_view(request):
    return render(request, 'users/home.html')



genai.configure(api_key=os.getenv('API'))

@login_required
def chatbot_view(request):
    return render(request, 'users/chatbot.html')

@csrf_exempt
@login_required
def chatbot_api(request):
    if request.method == 'POST':
        print("hi")
        try:
            data = json.loads(request.body)
            message = data.get('message', '')
            language = data.get('language', 'english')
            
            response = get_chatbot_response(message, language)
            
            audio_base64 = generate_tts_audio(response, language)
            
            return JsonResponse({
                'response': response,
                'audio': audio_base64
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_chatbot_response(message, language):
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        system_prompt = f"""
        You are a helpful farming assistant. Provide short, practical advice to farmers.
        Keep responses under 100 words. Focus on:
        - Crop management
        - Weather guidance  
        - Pest control
        - Soil health
        - Irrigation tips
        - Market information
        
        Respond in {"Hindi" if language == "hindi" else "English"}.
        Be encouraging and supportive.
        Please dont use any markdown send simple text as if will be interpreted differently by gttS it reads those quotations
        """
        
        full_prompt = f"{system_prompt}\n\nFarmer's question: {message}"
        
        response = model.generate_content(full_prompt)
        return response.text.strip()
        
    except Exception as e:
        fallback_msg = {
            'english': "I'm here to help with your farming questions. Please try again.",
            'hindi': "मैं आपके कृषि प्रश्नों में सहायता के लिए यहाँ हूँ। कृपया पुनः प्रयास करें।"
        }
        return fallback_msg.get(language, fallback_msg['english'])

def generate_tts_audio(text, language):
    try:
        lang_code = 'hi' if language == 'hindi' else 'en'
        tts = gTTS(text=text, lang=lang_code, slow=False)
        
        audio_buffer = io.BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        audio_base64 = base64.b64encode(audio_buffer.read()).decode('utf-8')
        return audio_base64
        
    except Exception as e:
        return None

@login_required
def bookkeeping_view(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        description = request.POST.get('description')
        entry_type = request.POST.get('type')
        amount = request.POST.get('amount')
        category = request.POST.get('category')

        if date and description and entry_type and amount:
            BookkeepingEntry.objects.create(
                user=request.user,
                date=date,
                description=description,
                type=entry_type,
                amount=amount,
                category=category or None  
            )
            return redirect('bookkeeping')  

    entries = BookkeepingEntry.objects.filter(user=request.user).order_by('-date')
    
    # Calculate statistics
    income_total = BookkeepingEntry.objects.filter(
        user=request.user, 
        type='income'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    expense_total = BookkeepingEntry.objects.filter(
        user=request.user, 
        type='expense'
    ).aggregate(total=Sum('amount'))['total'] or Decimal('0')
    
    net_balance = income_total - expense_total
    
    def format_amount(amount):
        if amount == int(amount):
            return int(amount)
        return amount
    
    context = {
        'entries': entries,
        'total_income': format_amount(income_total),
        'total_expense': format_amount(expense_total),
        'net_balance': format_amount(net_balance),
        'entries_count': entries.count(),
    }
    
    return render(request, 'users/bookkeeping.html', context)

@login_required
def market_prices_view(request):
    return render(request, 'users/market_prices.html')

@login_required
def livestock_tips_view(request):
    return render(request, 'users/livestock_tips.html')