from django.shortcuts import render,redirect
from django.views import View
from shop.models import Category,Product
from .forms import RegisterForm,LoginForm
from django.contrib import messages

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

class DetailView(View):
    def get(self,request,i):
        p = Product.objects.get(id=i)
        context = {'product':p}
        return render(request,'productdetail.html',context)


class Register(View):
    def get(self,request):
        form_instance = RegisterForm()
        context = {'form':form_instance}
        return render(request,'register.html',context)

    def post(self,request):
        form_instance = RegisterForm(request.POST)
        if form_instance.is_valid():
            form_instance.save()
            messages.success(request,"Registration successful !!")
            return redirect('login')
        return render(request,'register.html',{'form':form_instance})


from django.contrib.auth import authenticate,login,logout
class Login(View):
    def get(self,request):
        form_instance = LoginForm()
        context = {'form':form_instance}
        return render(request,'login.html',context)

    def post(self,request):
        form_instance = LoginForm(request.POST)
        if form_instance.is_valid():
            u = form_instance.cleaned_data['username']
            p = form_instance.cleaned_data['password']
            user = authenticate(username=u,password=p)
            if user and user.is_superuser:
                login(request,user)
                messages.success(request,'Login Successful')
                return redirect('shop:categoryview')
            elif user and user.is_superuser != True:
                login(request,user)
                messages.success(request,'Login Successful')
                return redirect('shop:categoryview')
            else:
                messages.error(request,'Invaild credentials')
        return render(request,'login.html',{'form':form_instance})

class Logout(View):
    def get(self,request):
        logout(request)
        return redirect('shop:login')



from shop.forms import CategoryForm,ProductForm
class AddCategoryView(View):
    def get(self,request):
        form_instance = CategoryForm()
        context = {'form':form_instance}
        return render(request,'addcategory.html',context)

    def post(self,request):
        form_instance = CategoryForm(request.POST,request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            messages.success(request, "Category Added Successfully !!")
            return render(request,'categories.html')
        return render(request, 'addcategory.html', {'form': form_instance})

class AddProductView(View):
    def get(self,request):
        form_instance = ProductForm()
        context = {'form':form_instance}
        return render(request,'addproducts.html',context)

    def post(self,request):
        form_instance = ProductForm(request.POST,request.FILES)
        if form_instance.is_valid():
            form_instance.save()
            messages.success(request, "Product Added Successfully !!")
            return render(request,'products.html')
        return render(request, 'addproducts.html', {'form': form_instance})


from shop.forms import StockForm
class AddStockView(View):
    def get(self,request,i):
        p = Product.objects.get(id=i)
        form_instance = StockForm(instance=p)
        context = {'form':form_instance}
        return render(request,'addstock.html',context)

    def post(self,request,i):
        p = Product.objects.get(id=i)
        form_instance = StockForm(request.POST,instance=p)
        if form_instance.is_valid():
            form_instance.save()
            messages.success(request, "Product Added Successfully !!")
            return redirect('shop:categoryview')
        return render(request, 'addstock.html', {'form': form_instance})


