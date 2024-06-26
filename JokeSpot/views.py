from django.shortcuts import render
from posts.models import Post
from categories.models import Category



def home(request, category_slug = None):
    data = Post.objects.all().order_by('-like')
    if category_slug is not None:
        category = Category.objects.get(slug = category_slug)
        data = Post.objects.filter(category  = category)
    categories = Category.objects.all()
    return render(request, 'home.html', {'data' : data, 'category' : categories})
def service(request, category_slug = None):
    data = Post.objects.all().order_by('-like')
    if category_slug is not None:
        category = Category.objects.get(slug = category_slug)
        data = Post.objects.filter(category  = category)
    categories = Category.objects.all()
    return render(request, 'service.html', {'data' : data, 'category' : categories})

def contact(request):
    return render(request, 'contact.html')
def about(request):
    return render(request, 'about.html')
