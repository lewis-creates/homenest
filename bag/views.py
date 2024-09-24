from django.shortcuts import (
    render,
    redirect,
    reverse,
    HttpResponse,
    get_object_or_404
)

def view_bag(request):
    """ A view that renders the bag contents page """

    return render(request, 'bag/bag.html')

def add_to_bag(request, item_id):
    """ Add a quantity of the specified product to the shopping bag """

    product = get_object_or_404(Product, pk=item_id)
    redirect_url = request.POST.get('redirect_url')
    bag = request.session.get('bag', {})

    try:
        quantity = int(request.POST.get('quantity'))
    except ValueError:
        messages.error(request, "Quantity must be a number between 1-99.")
        return redirect(reverse('product_detail', args=[item_id]))

    # Validate quantity
    if item_id in list(bag.keys()):
        current_quantity = bag[item_id]
        new_quantity = current_quantity + quantity
        if new_quantity > 99:
            bag[item_id] = 99
            messages.warning(request, f"Quantity for {product.name} has been"
                             " set to the maximum allowed value of 99.")
        else:
            bag[item_id] = new_quantity
            messages.success(request, f'Updated {product.name}'
                             f' quantity to {bag[item_id]}')
    else:
        if quantity > 99:
            quantity = 99
            messages.warning(request, f"Quantity for {product.name} has"
                             "been set to the maximum allowed value of 99.")
        elif quantity < 1:
            quantity = 1
            messages.warning(request, f"Quantity for {product.name}"
                             " has been set to the minimum allowed value"
                             " of 1.")
        bag[item_id] = quantity
        messages.success(request, f'Added {product.name} to your bag')

    request.session['bag'] = bag
    return redirect(redirect_url)


def adjust_bag(request, item_id):
    """
    Adjust the quantity of the specified product to the specified amount
    """

    product = get_object_or_404(Product, pk=item_id)
    bag = request.session.get('bag', {})

    try:
        quantity = int(request.POST.get('quantity'))
    except ValueError:
        messages.error(request, "Quantity must be a number between 1-99.")
        return redirect(reverse('view_bag'))

    # Validate quantity
    if quantity > 99:
        quantity = 99
        messages.warning(request, f"Quantity for {product.name}"
                         " has been set to the maximum allowed value"
                         " of 99.")
    elif quantity < 1:
        quantity = 1
        messages.warning(request, f"Quantity for {product.name}"
                         " has been set to the minimum allowed value of 1.")

    if quantity > 0:
        bag[item_id] = quantity
        messages.success(request, f'Updated {product.name} quantity'
                         f' to {bag[item_id]}')
    else:
        bag.pop(item_id)
        messages.success(request, f'Removed {product.name} from your bag')

    request.session['bag'] = bag
    return redirect(reverse('view_bag'))
