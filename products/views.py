from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.db.models.functions import Lower

from .models import Product, Category



def all_products(request):
    """  A view to show all products, including sorting and search queries """

    products = Product.objects.all()

    query = None
    categories = None
    sort = None
    direction = None

    if request.GET:
        # Handle sorting
        if 'sort' in request.GET:
            sortkey = request.GET['sort']
            sort = sortkey
            if sortkey == 'price':
                # Sort by price
                direction = request.GET.get('direction', 'asc')
                sort_by = 'price' if direction == 'asc' else '-price'
                products = products.order_by(sort_by)
            elif sortkey == 'rating':
                # Sort by rating (with products without ratings at the end)
                direction = request.GET.get('direction', 'desc')
                products = sort_by_rating(products, direction)
            elif sortkey == 'name':
                # Sort by product name
                direction = request.GET.get('direction', 'asc')
                sort_by = 'name' if direction == 'asc' else '-name'
                products = products.order_by(sort_by)
            elif sortkey == 'category':
                # Sort by category name
                direction = request.GET.get('direction', 'asc')
                sort_by = (
                    'category__name'
                    if direction == 'asc'
                    else '-category__name'
                )
                products = products.order_by(sort_by)

            # Handle category filtering
        if 'category' in request.GET:
            categories = request.GET['category'].split(',')
            products = products.filter(category__name__in=categories)
            categories = Category.objects.filter(name__in=categories)
                
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

    current_sorting = f'{sort}_{direction}' if sort and direction else None

    context = {
        'products': products,
        'search_term': query,
        'current_categories': categories,
        'current_sorting': current_sorting,
    }

    return render(request, 'products/products.html', context)


def sort_by_rating(products, direction):
    """
    Helper function to sort products by rating.
    Products with ratings are sorted by rating value,
    while products without ratings are placed at the end.
    """
    if direction == 'asc':
        products = products.annotate(
            avg_rating=Avg('reviews__rating')).order_by(F('avg_rating').asc(
                nulls_last=True)
        )
    else:
        products = products.annotate(
            avg_rating=Avg('reviews__rating')).order_by(F('avg_rating').desc(
                nulls_last=True)
        )

    return products



def product_detail(request, product_id):
    """ A view to show individual product details """

    product = get_object_or_404(Product, pk=product_id)

    context = {
        'product': product,
    }

    return render(request, 'products/product_detail.html', context)
