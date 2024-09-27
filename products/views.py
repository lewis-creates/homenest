from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Avg, F
from django.db.models.functions import Lower

from .models import Product, Category, Review
from .forms import ProductForm


def all_products(request):
    """ A view to show all products, including sorting and search queries """

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

    # Handle review deletion or submission
    if request.method == 'POST':
        if ('delete_review' in request.POST and
                request.POST.get('delete_review') == "true"):
            return handle_review_deletion(request, product)
        else:
            handle_review_submission(request, product)

    reviews = Review.objects.filter(product=product)

    context = {
        'product': product,
        'reviews': reviews,
    }

    return render(request, 'products/product_detail.html', context)


def handle_review_submission(request, product):
    """ Handle submission of a review for a product """

    # Get review details
    details = request.POST.get('details')
    rating = request.POST.get('rating')

    # Create or update the review
    if details:
        review, created = Review.objects.get_or_create(
            product=product,
            submitted_by=request.user,
            defaults={'rating': rating, 'details': details}
        )

        # Feedback to the user
        if created:
            messages.success(request, 'Your review was successfully created.')
        else:
            review.rating = rating
            review.details = details
            review.save()
            messages.info(request, 'Your existing review has been updated.')

    # Redirect back to product detail page
    return redirect(reverse('product_detail', args=[product.id]))


def handle_review_deletion(request, product):
    """ Handle deletion of a review for a product """

    review_id = request.POST.get('review_id')
    review = get_object_or_404(Review, id=review_id, product=product)

    # Check if review belongs to user or if user is superuser
    if review.submitted_by == request.user or request.user.is_superuser:
        # Delete the review
        review.delete()
        messages.success(request, 'Review was successfully deleted.')
    else:
        # Error message if no persmission is granted
        messages.error(request,
                       'You do not have permission to delete this review.')

    # Redirect back to the product detail page
    return redirect(reverse('product_detail', args=[product.id]))


@login_required
def add_product(request):
    """ Add a product """

    # Superuser check
    if not request.user.is_superuser:
        # Error message if user is not superuser
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    # Handle product addition
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            # Save new product
            product = form.save()
            messages.success(request, 'Successfully added product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            # Error message if form data is not valid
            messages.error(request,
                           'Failed to add product. Check the form is valid.')
    else:
        form = ProductForm()

    context = {
        'form': form,
    }

    return render(request, 'products/add_product.html', context)


@login_required
def edit_product(request, product_id):
    """ Edit a product """

    # Superuser check
    if not request.user.is_superuser:
        # Error message if user is not superuser
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)

    # Handle product editting
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # Save editted product
            form.save()
            messages.success(request, 'Successfully updated product!')
            return redirect(reverse('product_detail', args=[product.id]))
        else:
            # Error message if form data is not valid
            messages.error(request,
                           'Failed to update product. Ensure form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}')

    context = {
        'form': form,
        'product': product,
    }

    return render(request, 'products/edit_product.html', context)


@login_required
def delete_product(request, product_id):
    """ Delete a product """

    # Superuser check
    if not request.user.is_superuser:
        # Error message if user is not superuser
        messages.error(request, 'Sorry, only store owners can do that.')
        return redirect(reverse('home'))

    product = get_object_or_404(Product, pk=product_id)

    # Delete the product
    product.delete()
    messages.success(request, 'Product deleted!')

    return redirect(reverse('products'))