from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


class Category(models.Model):
    """
    Category model
    """
    class Meta:
        verbose_name_plural = 'Categories'

    name = models.CharField(max_length=254)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name


class Product(models.Model):
    """
    Product model
    """
    category = models.ForeignKey('Category', null=True,
                                 blank=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(default=0, max_digits=6,
                                 decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.name

    def update_rating(self):
        """ Update the product's rating based on the average of its reviews """
        reviews = self.reviews.all()
        if reviews.exists():
            total = sum(review.rating for review in reviews)
            self.rating = total / reviews.count()
        else:
            self.rating = None
        self.save()


class Review(models.Model):
    """
    Review model
    """
    product = models.ForeignKey(Product, related_name='reviews',
                                on_delete=models.CASCADE)
    details = models.TextField()
    rating = models.IntegerField(validators=[MinValueValidator(1),
                                 MaxValueValidator(5)])
    submitted_by = models.ForeignKey(User, related_name='reviews',
                                     on_delete=models.CASCADE)
    date_submitted = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review for {self.product} by {self.submitted_by}'


@receiver(post_save, sender=Review)
def update_product_rating_on_save(sender, instance, **kwargs):
    instance.product.update_rating()


@receiver(post_delete, sender=Review)
def update_product_rating_on_delete(sender, instance, **kwargs):
    instance.product.update_rating()