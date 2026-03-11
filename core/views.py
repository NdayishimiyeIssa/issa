from django.http import JsonResponse
from django.shortcuts import render
from core.models import Testing

def testing_view(request):
    # For now, return a simple static JSON response
    return JsonResponse({'message': 'Hello, world!'})

def health_check(request):
    return JsonResponse({'status': 'ok'})