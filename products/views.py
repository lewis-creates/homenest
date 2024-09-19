from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from .models import Product, Category



def all_products(request):
    """  A view to show all products, including sorting and search queries """

    products = Product.objects.all()

    query = None
    categories = None

    # Handle category filtering
    if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)

    if request.GET:
         # Handle search
        if 'q' in request.GET:
            query = request.GET['q']
            if query:
                products = products.filter(
                    Q(name__icontains=query) | Q(description__icontains=query)
                )
            else:
                messages.error(
                    request, "You didn't enter any search criteria!"
                )
                return redirect(reverse('products'))
                
    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
    }

    return render(request, 'products/products.html', context)


def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
