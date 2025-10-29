from django.shortcuts import render
from django.views import View
from shop.models import Category

class Categoryview(View):
    def get(self,request):
        c = Category.objects.all()
        context = {'categories':c}
        return render(request,'categories.html',context)

class ProductView(View):
    def get(self,request,i):
        c = Category.objects.get(id=i)
        context = {'category':c}
        return render(request,'products.html',context)