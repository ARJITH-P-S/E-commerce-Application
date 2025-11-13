from django.shortcuts import render,redirect
from django.views import View
from pyexpat.errors import messages
from shop.models import Product
from cart.models import Cart
from cart.forms import OrderForm
import razorpay




# Create your views here.
class AddtoCart(View):
    # Add items to cart
    def get(self,request,i):
        p = Product.objects.get(id=i)
        u = request.user
        try:
            c = Cart.objects.get(user=u,product=p) # check whether the product already placed by the current user
            c.quantity += 1 #or check whether the product is there in the Cart table
            c.save()          #if yes increments the quantity by 1
        except:
            c = Cart.objects.create(user=u,product=p,quantity=1) #else creates a new cart record inside Cart table
            c.save()
        return redirect('cart:cartview')

class CartView(View):
    # display items
    def get(self,request):
        u = request.user
        c = Cart.objects.filter(user=u)
        total = 0
        for i in c:
            total += i.product.price * i.quantity
        context = {'cart':c,'total':total}
        return render(request,'cart.html',context)

class Reduce(View):
    def get(self,request,i):
        u = request.user
        p = Product.objects.get(id=i)
        try:
            c = Cart.objects.get(user=u,product=p)
            if c.quantity > 0:
                c.quantity -= 1
                c.save()
            else:
                c.delete()
        except:
            pass
        return redirect('cart:cartview')

class DeleteCart(View):
    def get(self,request,i):
        u = request.user
        c = Cart.objects.get(id=i,user=u)
        c.delete()
        return redirect('cart:cartview')



def checkstock(c):
    stock = True
    for i in c:
        if i.product.stock < i.quantity:
            stock = False
            break
    else:
        stock = True
    return stock


from .models import Cart, Order, Order_items  # ✅ Ensure this line exists
from .forms import OrderForm                 # ✅ Import your form


import uuid
class CheckOut(View):
    def get(self, request):
        u = request.user
        c = Cart.objects.filter(user=u)
        stock = checkstock(c)
        if stock:
            form_instance = OrderForm()
            return render(request, 'checkout.html', {'form': form_instance})
        else:
            messages.error(request, "Currently no items available")
            return render(request, 'checkout.html')

    def post(self, request):
        form_instance = OrderForm(request.POST)
        if form_instance.is_valid():
            o = form_instance.save(commit=False)
            u = request.user
            o.user = u
            c = Cart.objects.filter(user=u)

            total = sum(i.product.price * i.quantity for i in c)
            o.amount = total
            o.save()

            context = {}

            print("Payment method selected:", o.payment_method)  # 🧠 Debug check

            if o.payment_method == "online":  # ✅ Matches 'online' from form
                # Razorpay client connection
                client = razorpay.Client(auth=('rzp_test_RdvGikY9c3cmme', 'p92bYksEVUlBtWNK18uykkwB'))
                response_payment = client.order.create(dict(amount=total * 100, currency="INR"))
                o.order_id = response_payment['id']
                o.save()
                context = {'payment': response_payment, 'method': 'online'}

            elif o.payment_method == "cod":  # ✅ Matches 'cod' from form
                o.is_ordered = True
                uid = uuid.uuid4().hex[:14]
                order_id = 'order_COD' + uid
                o.order_id = order_id
                o.save()

                order = Order.objects.get(order_id=order_id)
                for i in c:
                    order_item = Order_items.objects.create(order=order, product=i.product, quantity=i.quantity)
                    order_item.product.stock -= order_item.quantity
                    order_item.product.save()

                c.delete()

                context = {'order_id': order_id, 'payment_method': 'COD'}

            return render(request, 'payment.html', context)


from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.contrib.auth.models import User
from django.contrib.auth import login
from cart.models import Order

@method_decorator(csrf_exempt,name="dispatch")
class PaymentSuccess(View):
    def post(self,request,i): # here i represents the username
        # To add current user into current session again
        u = User.objects.get(username=i)
        login(request,u) #adds the user object u into session
        response = request.POST  #after payment razorpay sends payment details into the success view
        print(response)  # as response
        id=response['razorpay_order_id']
        print(id)

        # order
        order = Order.objects.get(order_id=id)
        order.is_ordered = True #after successful completion of order
        order.save()

        # order_items
        c = Cart.objects.filter(user=u)
        for i in c:
            o = Order_items.objects.create(order=order,product=i.product,quantity=i.quantity)
            o.save()
            o.product.stock = o.quantity
            o.product.save()

        # cart deletion
        c.delete()


        return render(request,'paymentsuccess.html')



class Orders(View):
    def get(self,request):
        u = request.user
        o = Order.objects.filter(user=u,is_ordered=True)
        context = {'orders':o}
        return render(request,'orders.html',context)