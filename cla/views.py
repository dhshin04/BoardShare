from django import forms
from django.forms import inlineformset_factory
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, HttpResponseForbidden
from django.template import loader
from django.contrib.auth.models import User 
from django.contrib.auth.views import LogoutView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import UserType
from .forms import ProfileUpdateForm, PatronCollectionsForm, LibrarianCollectionsForm
from .forms import LibrarianSignUpForm, PatronSignUpForm, ReviewsForm
from librarians.forms import LibrarianItemsForm
from django.views import generic
from django.http import JsonResponse
from django.db.models import Avg, Q
from librarians.models import *
from django.utils import timezone
from datetime import timedelta

def index(request):
    user = request.user #the user
    if not user.is_anonymous:
        try:
            user_type = UserType.objects.filter(email=user.email).first()

            # If librarian
            if not user_type:
                return redirect('cla:index')
            if user_type.is_librarian:
                return redirect('cla:librarianSearch')
            else:
                return redirect('cla:patronSearch')
        except:
            return redirect('cla:index')

    return render(request, 'cla/index.html')

def login(request):
    template_name = "cla/login.html"
    return render(request, 'cla/login.html')

def loginLibrarian(request):
    template_name = "cla/loginLibrarian.html"
    return render(request, 'cla/loginLibrarian.html')

def loginPatron(request):
    template_name = "cla/loginPatron.html"
    return render(request, 'cla/loginPatron.html')

def register(request):
    template_name = "cla/register.html"
    return render(request, 'cla/register.html')

def get_user_account(request) -> UserType:
    return UserType.objects.get(email=request.user.email)

def itemDisplay(request, item_id):
    template_name = "cla/itemDisplayPage.html"
    user = request.user #the user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:itemDisplayAnon', item_id=item_id)
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:itemDisplayPatron', item_id=item_id)
    except:
        return redirect('cla:index')

    item = get_object_or_404(LibrarianItem, id=item_id)
    similar_items = item.tags.similar_objects()
    # only gets the top three most similar games
    similar_items = similar_items[:3]
    reviews = Review.objects.filter(item=item)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    is_owner = item.owner == user

    collections_with_item = Collection.objects.filter(items=item)
    context = {
        'user': user,
        'item': item,
        'similar_items': similar_items,
        'collections': collections_with_item,
        'reviews': reviews,
        'average_rating': round(avg_rating, 1),
        'is_owner': is_owner,
        'carousel_item_id': f"carousel_{item.id}"
    }
    return render(request, 'cla/itemDisplayPage.html', context)

def deleteItem(request, item_id):
    user = request.user
    item = get_object_or_404(LibrarianItem, id=item_id)
    user_type = get_user_by_email(user.email)

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')
    
    if user == item.owner:
        # delete image from S3
        for image_obj in item.images.all():
            if image_obj.image and image_obj.image.name != 'boardgame_pics/default_boardgame.jpg':
                image_obj.image.delete(save=False)
            image_obj.delete()  # delete the image record

        item.delete()   
        return redirect('cla:librarianSearch')
    return render(request, 'cla/genericHttpResponse.html', {'message': 'You must be the owner of the item to delete it.'})

def itemDisplayAnon(request, item_id):
    template_name = "cla/itemDisplayAnon.html"

    user = request.user

    # If anonymous user
    if not user.is_anonymous:    
        try:
            user_type = UserType.objects.filter(email=user.email).first()

            # If librarian
            if not user_type:
                return redirect('cla:index')
            if user_type.is_librarian:
                return redirect('cla:itemDisplay', item_id=item_id)
            else:
                return redirect('cla:itemDisplayPatron', item_id=item_id)
        except:
            return redirect('cla:index')

    item = get_object_or_404(LibrarianItem, id=item_id)
    similar_items = item.tags.similar_objects()
    similar_items = [       # Used ChatGPT to exclude items in private collections for similar objects
        similar_item for similar_item in similar_items
        if not similar_item.collection_set.filter(is_private=True).exists()
    ]
    # only gets the top three most similar games
    similar_items = similar_items[:3]
    reviews = Review.objects.filter(item=item)
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    collections_with_item = Collection.objects.filter(items=item, is_private=False)

    context = {
        'item': item,
        'similar_items': similar_items,
        'reviews': reviews,
        'average_rating': round(avg_rating, 1),
        'collections': collections_with_item,
        'carousel_item_id': f"carousel_{item.id}"
    }
    return render(request, 'cla/itemDisplayAnon.html', context)

def itemDisplayPatron(request, item_id):
    template_name = "cla/itemDisplayPagePatron.html"
    user = request.user #the user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:itemDisplayAnon', item_id=item_id)
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:itemDisplay', item_id=item_id)
    except:
        return redirect('cla:index')

    # old logic, this didnt ensure visible "private" items could be seen, we have to add them back!
    # item = get_object_or_404(LibrarianItem, id=item_id)
    # similar_items = item.tags.similar_objects()
    # similar_items = [       # Used ChatGPT to exclude items in private collections for similar objects
    #     similar_item for similar_item in similar_items
    #     if not similar_item.collection_set.filter(is_private=True).exists()
    # ]
    # # only gets the top three most similar games
    # similar_items = similar_items[:3]

    # Used ChatGPT to help create the set() in order to add back the visible options, but overall logic was my own
    item = get_object_or_404(LibrarianItem, id=item_id)
    similar_items = item.tags.similar_objects()

    # get visible items (all)
    visible_items = set()
    for i in LibrarianItem.objects.all():
        visible_items.add(i)

    # remove private collection items
    for c in Collection.objects.filter(is_private=True):
        for private_item in c.items.all():
            if private_item in visible_items:
                visible_items.remove(private_item)

    # then add back items the user has access to which could be in private
    for c in Collection.objects.filter(visible_to=user):
        for accessible_item in c.items.all():
            visible_items.add(accessible_item)

    # filter similar_items that are in the visible ones
    filtered_similar_items = [i for i in similar_items if i in visible_items]

    # keep top 3 after filtering
    filtered_similar_items = filtered_similar_items[:3]

    reviews = Review.objects.filter(item=item)
    is_owner = item.owner == user
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    collections_with_item = Collection.objects.filter(items=item)

    previous_review = Review.objects.filter(user=user, item=item).first()

    if request.method == 'POST':
        if previous_review:     # update previous review if exists instead of creating new one
            review_form = ReviewsForm(request.POST, instance=previous_review)
        else:
            review_form = ReviewsForm(request.POST)

        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.user = user
            review.item = item
            review.save()
            messages.success(request, 'Review created successfully')
            return redirect('cla:itemDisplayPatron', item_id=item_id)
    else:
        review_form = ReviewsForm()

    user_has_approved_request = ItemAccessRequest.objects.filter(
        item=item, patron=request.user, status='approved'
    ).exists()

    context = {
        'item': item,
        'similar_items': filtered_similar_items,
        'user_has_approved_request': user_has_approved_request,
        'reviews': reviews,
        'form': review_form,
        'average_rating': round(avg_rating, 1),
        'collections': collections_with_item,
        'is_owner': is_owner,
        'carousel_item_id': f"carousel_{item.id}"
    }
    return render(request, 'cla/itemDisplayPagePatron.html', context)

# old function that would add an item to collection - NOT IN USE - replaced by addItemToCollectionSubmit
def addToCollection(request):
    if request.user.is_anonymous:
        return redirect('cla:index')
    
    if request.method == "POST":
        collection_id = request.POST.get("collection_id")
        item_id = request.POST.get("item_id")

        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
        item = get_object_or_404(LibrarianItem, id=item_id)

        collection.items.add(item)
        return JsonResponse({"success": True, "message": f"'{item.title}' added to '{collection.name}'."})

    user_collections = Collection.objects.filter(owner=request.user)

    if not user_collections:
        return render(request, "cla/addToCollectionPopup.html", {"message": "You have no collections. Please create one first."})

    return render(request, "cla/addToCollectionPopup.html", {"collections": user_collections})

# helper function
def redirect_to_item_display(item_id, user_account):
    if user_account.is_librarian:
        return redirect('cla:itemDisplay', item_id=item_id)
    else:
        return redirect('cla:itemDisplayPatron', item_id=item_id)

def redirect_to_collection_display(collection_id, user_account):
    if user_account.is_librarian:
        return redirect('cla:publicCollectionDisplay', collection_id=collection_id)
    else:
        return redirect('cla:publicCollectionDisplayPatron', collection_id=collection_id)
    
# Formset definition - added explicit DELETE widget
ImageFormSet = inlineformset_factory(
    LibrarianItem,
    LibrarianItemImage,
    fields=('image',),
    extra=1,
    can_delete=True,
    widgets={
        'image': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        'DELETE': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
    }
)

# Keep this view for fetching the modal content
def editItem(request, item_id):

    if request.user.is_anonymous:
        return redirect('cla:index')

    item = get_object_or_404(LibrarianItem, id=item_id)
    form = LibrarianItemsForm(instance=item)
    formset = ImageFormSet(instance=item)
    
    return render(request, 'cla/editItem.html', {
        'form': form,
        'formset': formset,
        'item': item,
    })

def editItemSubmit(request, item_id):
    user_account = get_user_account(request)
    item = get_object_or_404(LibrarianItem, id=item_id)

    if item.owner != request.user:
        messages.error(request, "You do not have permission to edit this item.")
        return redirect_to_item_display(item.id, user_account)

    if request.method == "POST":
        form = LibrarianItemsForm(request.POST, request.FILES, instance=item)
        formset = ImageFormSet(request.POST, request.FILES, instance=item)

        if form.is_valid() and formset.is_valid():
            form.save()
            
            # Process the formset including deletions
            instances = formset.save(commit=False)
            
            # Process any deleted forms first
            for obj in formset.deleted_objects:
                if obj.image and obj.image.name != 'boardgame_pics/default_boardgame.jpg':
                    obj.image.delete(save=False)  # Deletes from AWS or wherever you're storing media
                obj.delete()
                
            # Save new and modified instances
            for instance in instances:
                instance.save()
            
            # Save many-to-many relationships if any
            formset.save_m2m()
            
            messages.success(request, "Item updated successfully.")
            return redirect_to_item_display(item.id, user_account)

        messages.error(request, "Please correct the errors below.")
        return render(request, "cla/editItem.html", {
            'form': form,
            'formset': formset,
            'item': item,
        })

    # If it's not a POST request, redirect to editItem view
    return redirect('cla:editItem', item_id=item.id)
    
def deleteItem(request, item_id):
    template_name = 'cla/deleteItem.html'
    item = get_object_or_404(LibrarianItem, id=item_id)
    user_account = get_user_account(request)

    if item.owner != request.user:
        messages.error(request, "You do not have permission to delete this item.")
        return redirect_to_item_display(item.id, user_account)

    context = {
        'item': item,
    }
    return render(request, template_name, context)

def deleteItemSubmit(request, item_id):
    user_account = get_user_account(request)
    item = get_object_or_404(LibrarianItem, id=item_id)

    if item.owner != request.user:
        messages.error(request, "You do not have permission to delete this item.")
        return redirect_to_item_display(item.id, user_account)

    if request.method == "POST":
        typed_name = request.POST.get("confirm_name", "")
        if typed_name == item.title:
            for image_obj in item.images.all():
                if image_obj.image and image_obj.image.name != 'boardgame_pics/default_boardgame.jpg':
                    image_obj.image.delete(save=False)
                image_obj.delete()  # delete the image record
            item.delete()
            messages.success(request, f'"{item.title}" was successfully deleted.')
            return redirect("cla:viewMyGames")  
        else:
            messages.warning(request, "The item name you entered does not match.")

    return redirect_to_item_display(item.id, user_account)

def addItemToCollection(request, item_id):
    template_name = 'cla/addItemToCollection.html'

    if request.user.is_anonymous:
        return redirect('cla:index')

    item = get_object_or_404(LibrarianItem, id=item_id)
    user_collections = Collection.objects.filter(owner=request.user)
    user_account = get_user_account(request)

    if not user_collections:
        # messages.warning(request, "You do not own any collections yet. Create one before trying to add an item to a collection.")
        return render(request, 'cla/genericHttpResponse.html', {'message': 'You do not own any collections yet. Create one before trying to add an item to a collection.'})
    
    context = {
        'collections': user_collections,
        'item': item,
    }

    return render(request, template_name, context)

def addItemToCollectionSubmit(request, item_id):
    if request.user.is_anonymous:
        return redirect('cla:index')

    user_account = get_user_account(request)

    if request.method == "POST":
        collection_id = request.POST.get("collection_id")
        item = get_object_or_404(LibrarianItem, id=item_id)
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
        if collection.items.filter(id=item.id).exists():
            messages.warning(request, "Item is already in this collection.")
            # return redirect('cla:itemDisplay', item_id=item.id)  
            return redirect_to_item_display(item.id, user_account)
        else:

            # check if item is already in a private collection
            for private_c in Collection.objects.filter(is_private=True):
                for i in private_c.items.all():
                    if(i.id == item_id):
                        messages.warning(request, "Item is currently in private collection " + str(private_c.name) + " and cannot be added.")
                        return redirect('cla:itemDisplay', item_id=item.id)  

            # if not, add
            collection.items.add(item)
            collection.save()

            # if the item is being added to a private collection, remove from all other collections
            if collection.is_private:
                for c in Collection.objects.all():
                    for i in c.items.all():
                        #print(f"This collection: {collection_id}, Collection: {c.id}")

                        # if this item exists within another collection
                        if((i.id == item_id) and (int(c.id) != int(collection_id))):
                            # remove it
                            c.items.remove(item)
                    c.save()

            messages.success(request, "Item added to collection successfully.")
        
        return redirect_to_item_display(item.id, user_account)
        # return redirect('cla:itemDisplay', item_id=item.id)  

def deleteItemFromCollection(request, item_id):
    template_name = 'cla/deleteItemFromCollection.html'

    if request.user.is_anonymous:
        return redirect('cla:index')

    item = get_object_or_404(LibrarianItem, id=item_id)
    user_collections = Collection.objects.filter(owner=request.user, items=item)

    if not user_collections:
        return render(request, 'cla/genericHttpResponse.html', {'message': "This item is not in any collections you own."})
    
    context = {
        'collections': user_collections,
        'item': item,
    }

    return render(request, template_name, context)

def deleteItemFromCollectionSubmit(request, item_id):
    if request.user.is_anonymous:
        return redirect('cla:index')

    user_account = get_user_account(request)

    if request.method == "POST":
        collection_id = request.POST.get("collection_id")
        item = get_object_or_404(LibrarianItem, id=item_id)
        collection = get_object_or_404(Collection, id=collection_id, owner=request.user)
        collection.items.remove(item)
        collection.save()
        messages.success(request, "Item deleted from collection successfully.")
        return redirect_to_item_display(item.id, user_account)

def singleCollectionSearch(request, collection_id):
    collection = get_object_or_404(Collection, id=collection_id)
    user = request.user

    access_requests = CollectionAccessRequest.objects.filter(
        collection=collection, status='pending'
    ) if request.user == collection.owner else None

    # Start with all visible users
    visible_users = list(collection.visible_to.all())

    # Remove librarians based on UserType
    patrons_with_access = [
        user for user in visible_users
        if not (get_user_by_email(user.email) and get_user_by_email(user.email).is_librarian)
    ]

    return render(request, 'singleCollectionSearch.html', {
        'collection': collection,
        'collection_id': collection_id,
        'access_requests': access_requests,
        'patrons_with_access': patrons_with_access,
    })

def editCollection(request, collection_id):
    template_name = 'cla/editCollection.html'

    if request.user.is_anonymous:
        return redirect('cla:index')

    collection = get_object_or_404(Collection, id=collection_id)
    user_account = get_user_account(request)
    form = None
    if user_account.is_librarian:
        form = LibrarianCollectionsForm(instance=collection)
    else:
        form = PatronCollectionsForm(instance=collection)
    
    context = {
        'collection': collection,
        'form': form,
    }

    return render(request, template_name, context)

def editCollectionSubmit(request, collection_id):
    user_account = get_user_account(request)
    collection = get_object_or_404(Collection, id=collection_id)

    if collection.owner != request.user:
        messages.error(request, "You do not have permission to edit this collection.")
        return redirect_to_collection_display(collection.id, user_account)

    if request.method == "POST":
        form = None
        if user_account.is_librarian:
            form = LibrarianCollectionsForm(request.POST, request.FILES, instance=collection)
        else:
            form = PatronCollectionsForm(request.POST, request.FILES, instance=collection)
        if form.is_valid():
            form.save()
            messages.success(request, "Collection updated successfully.")
            return redirect_to_collection_display(collection.id, user_account)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = LibrarianItemsForm(instance=collection.id)
        
        return redirect_to_item_display(collection.id, user_account)
    
def deleteCollection(request, collection_id):
    template_name = 'cla/deleteCollection.html'
    collection = get_object_or_404(Collection, id=collection_id)
    user_account = get_user_account(request)

    if collection.owner != request.user:
        messages.error(request, "You do not have permission to delete this item.")
        return redirect_to_item_display(collection.id, user_account)
    
    context = {
        'collection': collection,
    }

    return render(request, template_name, context)

def deleteCollectionSubmit(request, collection_id):
    user_account = get_user_account(request)
    collection = get_object_or_404(Collection, id=collection_id)

    if collection.owner != request.user:
        messages.error(request, "You do not have permission to delete this collection.")
        return redirect_to_collection_display(collection.id, user_account)

    if request.method == "POST":
        typed_name = request.POST.get("confirm_name", "")
        if typed_name == collection.name:
            collection.delete()
            messages.success(request, f'"{collection.name}" was successfully deleted.')
            if user_account.is_librarian:
                return redirect("cla:viewCollectionsLibrarian")
            else:
                return redirect("cla:viewCollectionsPatron")
        else:
            messages.warning(request, "The collection name you entered does not match.")
    
    return redirect_to_collection_display(collection.id, user_account)

def publicCollectionDisplay(request, collection_id):
    template_name = "cla/singleCollectionSearch.html"

    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    collection = get_object_or_404(Collection, id=collection_id)
    items = collection.items.all()
    visible_users = list(collection.visible_to.all())
    is_owner = request.user == collection.owner

    patrons_with_access = [
        user for user in visible_users
        if not (get_user_by_email(user.email) and get_user_by_email(user.email).is_librarian)
    ]
    return render(request, 'cla/singleCollectionSearch.html', {'collection': collection, 'items': items, 'patrons_with_access': patrons_with_access, 'is_owner': is_owner})

def publicCollectionDisplayPatron(request, collection_id):
    template_name = "cla/singleCollectionSearchPatron.html"

    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:librarianSearch')
    except:
        return redirect('cla:index')

    collection = get_object_or_404(Collection, id=collection_id)
    items = collection.items.all()
    visible_users = list(collection.visible_to.all())
    is_owner = request.user == collection.owner

    patrons_with_access = [
        user for user in visible_users
        if not (get_user_by_email(user.email) and get_user_by_email(user.email).is_librarian)
    ]
    return render(request, 'cla/singleCollectionSearchPatron.html', {'collection': collection, 'items': items, 'patrons_with_access': patrons_with_access, 'is_owner': is_owner})

def publicCollectionDisplayAnon(request, collection_id):
    template_name = "cla/singleCollectionSearchAnon.html"
    user = request.user

    if not user.is_anonymous:
        try:
            user_type = UserType.objects.filter(email=user.email).first()

            # Error
            if not user_type:
                return redirect('cla:index')
            
            if user_type.is_librarian:      # if librarian
                return redirect('cla:librarianSearch')
            else:                           # if patron
                return redirect('cla:patronSearch')
        except:
            return redirect('cla:index')

    collection = get_object_or_404(Collection, id=collection_id)
    items = []
    for i in collection.items.all():
        items.append(i)
    # remove any items that are in a private collection because anon doesn't have access to that
    for private_collection in Collection.objects.filter(is_private = True):
        for i in private_collection.items.all():
            if i in items:
                items.remove(i)

    visible_users = list(collection.visible_to.all())

    patrons_with_access = [
        user for user in visible_users
        if not (get_user_by_email(user.email) and get_user_by_email(user.email).is_librarian)
    ]
    return render(request, 'cla/singleCollectionSearchAnon.html', {'collection': collection, 'items': items, 'patrons_with_access': patrons_with_access})

def searchCollectionAnon(request, collection_id):  
    user = request.user

    if not user.is_anonymous:
        try:
            user_type = UserType.objects.filter(email=user.email).first()

            # Error
            if not user_type:
                return redirect('cla:index')
            
            if user_type.is_librarian:      # if librarian
                return redirect('cla:librarianSearch')
            else:                           # if patron
                return redirect('cla:patronSearch')
        except:
            return redirect('cla:index')

    collection = get_object_or_404(Collection, id=collection_id)
    items = collection.items.all()
    visible_users = list(collection.visible_to.all())

    query = request.GET.get('search', '').strip()
    selected_filter = request.GET.get('filter', 'all')

    collection = get_object_or_404(Collection, id=collection_id)

    # Start with just items in this collection
    items = collection.items.all()

    # Apply search query within the collection items
    # Django Q class usage: https://docs.djangoproject.com/en/5.1/topics/db/queries/
    if query:
        items = items.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(status__icontains=query) |
            Q(owner__username__icontains=query)
        )

    # Apply filters (only on the items within this collection)
    if selected_filter == "five-star":
        items = items.annotate(avg_rating=Avg('review__rating')).filter(avg_rating=5)
        if query:
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(status__icontains=query) |
                Q(owner__username__icontains=query)
            )
    elif selected_filter == "collections":
        items = []
    elif selected_filter == "boardgames":
        pass
    elif selected_filter == "private" or selected_filter == "public":
        items = []
    
    patrons_with_access = [
            user for user in visible_users
            if not (get_user_by_email(user.email) and get_user_by_email(user.email).is_librarian)
        ]
    
    context = {
        'collection': collection,
        'items': items,
        'selected_filter': selected_filter,
        'patrons_with_access': patrons_with_access,
    }
    return render(request, 'cla/singleCollectionSearchAnon.html', context)

def searchCollection(request, collection_id):    
    user = request.user

    if user.is_anonymous:
        return redirect('cla:index')

    collection = get_object_or_404(Collection, id=collection_id)
    items = collection.items.all()
    visible_users = list(collection.visible_to.all())

    query = request.GET.get('search', '').strip()
    selected_filter = request.GET.get('filter', 'all')

    collection = get_object_or_404(Collection, id=collection_id)

    # Same logic as above: just for different user (regular user)
    # Start with just items in this collection
    items = collection.items.all()

    # Apply search query within the collection items
    # Django Q class usage: https://docs.djangoproject.com/en/5.1/topics/db/queries/
    if query:
        items = items.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(status__icontains=query) |
            Q(owner__username__icontains=query)
        )

    # Apply filters (only on the items within this collection)
    if selected_filter == "five-star":
        items = items.annotate(avg_rating=Avg('review__rating')).filter(avg_rating=5)
        if query:
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(status__icontains=query) |
                Q(owner__username__icontains=query)
            )
    elif selected_filter == "collections":
        items = []
    elif selected_filter == "boardgames":
        pass
    elif selected_filter == "private" or selected_filter == "public":
        items = []
    
    patrons_with_access = [
            user for user in visible_users
            if not (get_user_by_email(user.email) and get_user_by_email(user.email).is_librarian)
        ]
    
    context = {
        'collection': collection,
        'items': items,
        'selected_filter': selected_filter,
        'patrons_with_access': patrons_with_access,
    }

    userAccount = get_user_by_email(user.email)
    if userAccount.is_librarian:
        return render(request, 'cla/singleCollectionSearch.html', context)
    else:
        return render(request, 'cla/singleCollectionSearchPatron.html', context)

def addCollection(request):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')


    if request.method == 'POST':
        collection_form = LibrarianCollectionsForm(request.POST)
        if collection_form.is_valid():
            collection = collection_form.save(commit=False)
            collection.owner = request.user

            # updating list of users depending on privacy
            is_private = request.POST.get('is_private')

            # save collection before updating many-to-many field
            collection.save()

            # for user in User.objects.all():
            #     userGmail = user.email #their email
            #     userAccount = get_user_by_email(userGmail)
            #     # if the user has signed up for an account
            #     if userAccount:
            #         # add everyone
            #         collection.visible_to.add(user)
            #         # remove patron access if the collection is private
            #         if (is_private) and (userAccount.is_librarian == False):
            #             collection.visible_to.remove(user)

            if collection.is_private:
                # add all librarians to visible_to
                librarian_emails = UserType.objects.filter(is_librarian=True).values_list('email', flat=True)
                librarian_users = User.objects.filter(email__in=librarian_emails)
                collection.visible_to.set(librarian_users)
            else:
                # public collection — everyone has access
                collection.visible_to.set(User.objects.all())

            '''
            usersthatview = collection.visible_to.all()
            for u in usersthatview:
                print(u)
                userAccount = get_user_by_email(u.email)
                print(userAccount.is_librarian)
            '''

            collection.save()
            messages.success(request, 'Collection created successfully')
            return redirect('cla:addCollectionPatron')
    else:
        collection_form = LibrarianCollectionsForm()

    return render(
        request, 
        'cla/addCollection.html', 
        {
            'form': collection_form,
            'user': request.user,
        }
    )

def addCollectionPatron(request):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:addCollection')
    except:
        return redirect('cla:index')

    if request.method == 'POST':
        collection_form = PatronCollectionsForm(request.POST)
        if collection_form.is_valid():
            collection = collection_form.save(commit=False)
            collection.owner = request.user
            collection.save()

            for user in User.objects.all():
                userGmail = user.email
                userAccount = get_user_by_email(userGmail)
                # if the user has signed up for an account
                if userAccount:
                    # add everyone since patrons can only create public collections
                    collection.visible_to.add(user)

            collection.save()
            messages.success(request, 'Collection created successfully')
            return redirect('cla:addCollectionPatron')
    else:
        collection_form = PatronCollectionsForm()

    return render(
        request, 
        'cla/addCollectionPatron.html', 
        {
            'form': collection_form,
            'user': request.user,
        }
    )

# whole search page content
def search(request):        
    user = request.user

    # anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    userAccount = get_user_by_email(user.email)

    query = request.GET.get('search', '').strip()
    selected_filter = request.GET.get('filter', 'all')
    selected_tag = request.GET.get('tag', '').strip()

    items = LibrarianItem.objects.all()
    public_collections = Collection.objects.filter(is_private=False)
    private_collections = Collection.objects.filter(is_private=True)
    accessible_collections = Collection.objects.filter(visible_to=user)

    if not userAccount.is_librarian:
        items = []
        for i in LibrarianItem.objects.all():
            # default add all items
            items.append(i)

        # if an item is in a private collection, remove it
        for c in Collection.objects.filter(is_private=True):
            for item in c.items.all():
                items.remove(item)

        # but add it back again if the user has access to it
        for c in Collection.objects.filter(visible_to=user):
            for item in c.items.all():
                if item not in items:
                    items.append(item)

    # Django Q class usage: https://docs.djangoproject.com/en/5.1/topics/db/queries/
    if query:
        items = items.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(status__icontains=query) |
            Q(owner__username__icontains=query)
        )

        collections = Collection.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(owner__username__icontains=query)
        )

        public_collections = collections.filter(is_private=False)
        private_collections = collections.filter(is_private=True)

    if selected_filter == "boardgames":
        public_collections = []
        private_collections = []
    elif selected_filter == "collections":
        items = []
    elif selected_filter == "private":
        items = []
        public_collections = []
    elif selected_filter == "public":
        items = []
        private_collections = []
    elif selected_filter == "five-star":
        if not userAccount.is_librarian:
            items = []
            for i in LibrarianItem.objects.all():
                items.append(i)

            # if an item is in a private collection, remove it
            for c in Collection.objects.filter(is_private=True):
                for item in c.items.all():
                    items.remove(item)

            # but add it back again if the user has access to it
            for c in Collection.objects.filter(visible_to=user):
                for item in c.items.all():
                    if item not in items:
                        items.append(item)

        # filter out the items that are not 5-star rated
        items = [item for item in items if item.review_set.aggregate(avg_rating=Avg('rating'))['avg_rating'] == 5]
        if query:
            # query again in the five star since we get a new list of items (overwrites first item call)
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(status__icontains=query) |
                Q(owner__username__icontains=query)
            )
        public_collections = []
        private_collections = []
    elif selected_filter == "tag":
        if not userAccount.is_librarian:
            items = []
            for i in LibrarianItem.objects.all():
                # default add all items
                items.append(i)

            # if an item is in a private collection, remove it
            for c in Collection.objects.filter(is_private=True):
                for item in c.items.all():
                    items.remove(item)

            # but add it back again if the user has access to it
            for c in Collection.objects.filter(visible_to=user):
                for item in c.items.all():
                    if item not in items:
                        items.append(item)
        
        # filter for tags now
        items = [item for item in items if selected_tag in [tag.name for tag in item.tags.all()]]
        if query:
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(status__icontains=query) |
                Q(owner__username__icontains=query)
            )
        public_collections = []
        private_collections = []

    context = {
        'user': user,
        'items': items,
        'public_collections': public_collections,
        'private_collections': private_collections,
        'selected_filter': selected_filter,
        'accessible_collections': accessible_collections,
    }

    userAccount = get_user_by_email(user.email)
    if userAccount.is_librarian:
        context = {
            'user': user,
            'items': items,
            'public_collections': public_collections,
            'private_collections': private_collections,
            'selected_filter': selected_filter,
        }
        return render(request, "cla/librarianSearch.html", context)
    else:
        return render(request, "cla/patronSearch.html", context)
    
def searchAnon(request):        
    user = request.user

    if not user.is_anonymous:
        try:
            user_type = UserType.objects.filter(email=user.email).first()

            # error
            if not user_type:
                return redirect('cla:index')
            
            if user_type.is_librarian:      # if librarian
                return redirect('cla:librarianSearch')
            else:                           # if patron
                return redirect('cla:patronSearch')
        except:
            return redirect('cla:index')

    query = request.GET.get('search', '').strip()
    selected_filter = request.GET.get('filter', 'all')
    selected_tag = request.GET.get('tag', '').strip()

    items = LibrarianItem.objects.all().exclude(collection__is_private=True)
    public_collections = Collection.objects.filter(is_private=False)

    if query:
        # Django Q class usage: https://docs.djangoproject.com/en/5.1/topics/db/queries/
        items = items.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(location__icontains=query) |
            Q(status__icontains=query) |
            Q(owner__username__icontains=query)
        )

        collections = Collection.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(owner__username__icontains=query)
        )

        public_collections = collections.filter(is_private=False)

    if selected_filter == "boardgames":
        public_collections = []
    elif selected_filter == "collections":
        items = []
    elif selected_filter == "public":
        items = []
    elif selected_filter == "five-star":
        items = LibrarianItem.objects.annotate(avg_rating=Avg('review__rating')).filter(avg_rating=5).exclude(collection__is_private=True)
        if query:
            # query again in the five star since we get a new list of items (overwrites first item call)
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(status__icontains=query) |
                Q(owner__username__icontains=query)
            )
        public_collections = []
    elif selected_filter == "tag":
        items = LibrarianItem.objects.filter(tags__name__in=[selected_tag]).exclude(collection__is_private=True)
        if query:
            items = items.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query) |
                Q(status__icontains=query) |
                Q(owner__username__icontains=query)
            )
        public_collections = []

    context = {
        'items': items,
        'public_collections': public_collections,
        'selected_filter': selected_filter,
    }
    return render(request, 'cla/anonymous.html', context)

def anonymousSearch(request):
    template_name = "cla/anonymous.html"

    user = request.user
    # If not anonymous user
    if not user.is_anonymous:
        try:
            user_type = UserType.objects.filter(email=user.email).first()

            # Error
            if not user_type:
                return redirect('cla:index')
            
            if user_type.is_librarian:      # if librarian
                return redirect('cla:librarianSearch')
            else:                           # if patron
                return redirect('cla:patronSearch')
        except:
            return redirect('cla:index')

    public_collections = Collection.objects.filter(is_private=False)
    items = []
    for i in LibrarianItem.objects.all():
        # default add all items
        items.append(i)

    # if an item is in a private collection, remove it
    for c in Collection.objects.filter(is_private=True):
        for item in c.items.all():
            items.remove(item)

    context = {
        'items': items,
        'public_collections': public_collections,
    }
    return render(request, 'cla/anonymous.html', context)

def patronSearch(request):
    template_name = "cla/patronSearch.html"
    user = request.user
    #items = LibrarianItem.objects.all()

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:librarianSearch')
    except:
        return redirect('cla:index')

    public_collections = Collection.objects.filter(is_private=False)
    private_collections = Collection.objects.filter(is_private=True)

    accessible_collections = Collection.objects.filter(visible_to=user)

    items = []
    for i in LibrarianItem.objects.all():
        # default add all items
        items.append(i)

    # if an item is in a private collection, remove it
    for c in Collection.objects.filter(is_private=True):
        for item in c.items.all():
            items.remove(item)

    # but add it back again if the user has access to it
    for c in Collection.objects.filter(visible_to=user):
        for item in c.items.all():
            if item not in items:
                items.append(item)

    new_notifications = Notification.objects.filter(user=user, is_read=False).exists()

    context = {
        'user': user,
        'items': items,
        'public_collections': public_collections,
        'private_collections': private_collections,
        'accessible_collections': accessible_collections,
        'new_notifications': new_notifications
    }
    return render(request, 'cla/patronSearch.html', context)


def librarianSearch(request):
    template_name = "cla/librarianSearch.html"
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    items = LibrarianItem.objects.all()
    public_collections = Collection.objects.filter(is_private=False)
    private_collections = Collection.objects.filter(is_private=True)
    pending_requests = (
        CollectionAccessRequest.objects.filter(collection__owner=user, status='pending').exists() or
        ItemAccessRequest.objects.filter(item__owner=user, status='pending').exists() or
        ItemReturnRequest.objects.filter(item__owner=user, status='pending').exists() or
        AccountUpgradeRequest.objects.filter(status='pending').exists()
    )
    context = {
        'user': user,
        'items': items,
        'public_collections': public_collections,
        'private_collections': private_collections,
        'pending_requests': pending_requests
    }
    return render(request, 'cla/librarianSearch.html', context)

def viewCollectionsPatron(request):
    template_name = "cla/viewCollectionsPatron.html"
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:viewCollectionsLibrarian')
    except:
        return redirect('cla:index')

    my_collections = Collection.objects.filter(owner=user)
    context = {
        'user': user,
        'my_collections': my_collections,
    }
    return render(request, 'cla/viewCollectionsPatron.html', context)

def viewCollectionsLibrarian(request):
    template_name = "cla/viewCollectionsLibrarian.html"
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:viewCollectionsPatron')
    except:
        return redirect('cla:index')

    my_collections = Collection.objects.filter(owner=user)
    public_collections = my_collections.filter(is_private=False)
    private_collections = my_collections.filter(is_private=True)
    context = {
        'user': user,
        'public_collections': public_collections,
        'private_collections': private_collections,
    }
    return render(request, 'cla/viewCollectionsLibrarian.html', context)

def requestAccess(request, collection_id):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:librarianSearch')
    except:
        return redirect('cla:index')

    # https://docs.djangoproject.com/en/5.2/ref/request-response/
    # https://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python
    # using json for ease in transferring information, as this is a helper function and not actually sending a view
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method. Please try again.'}, status=400)
    
    collection = get_object_or_404(Collection, id=collection_id)

    if CollectionAccessRequest.objects.filter(patron=user, collection=collection, status='pending').exists():
        return JsonResponse({'message': 'Request already sent.'}, status=400)

    access_request = CollectionAccessRequest.objects.create(patron=user, collection=collection)
    return JsonResponse({'message': 'Access request submitted.'}, status=200)

def manageAccessRequests(request):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    requests = CollectionAccessRequest.objects.filter(collection__owner=user, status='pending')
    item_requests = ItemAccessRequest.objects.filter(item__owner=user, status='pending')
    return_requests = ItemReturnRequest.objects.filter(item__owner=user, status='pending')
    upgrade_requests = AccountUpgradeRequest.objects.filter(status='pending')

    CollectionAccessRequest.objects.filter(collection__owner=user, status='pending').update(is_read=True)
    ItemAccessRequest.objects.filter(item__owner=user, status='pending').update(is_read=True)
    ItemReturnRequest.objects.filter(item__owner=user, status='pending').update(is_read=True)
    for upgrade_request in upgrade_requests:
        upgrade_request.mark_as_read(user=user)
    return render(request, 'cla/manageAccessRequests.html', {
        'requests': requests,
        'item_requests': item_requests,
        'return_requests': return_requests,
        'upgrade_requests': upgrade_requests,
    })
    #return render(request, 'cla/manageAccessRequests.html', {'requests': requests})


def handleAccessRequest(request, request_id, decision):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    access_request = get_object_or_404(CollectionAccessRequest, id=request_id, collection__owner=request.user)
    collection = access_request.collection
    if decision == 'approve':
        access_request.status = 'approved'
        if collection.is_private:
            collection.visible_to.add(access_request.patron)
        # access_request.collection.visible_to.add(access_request.patron)
    elif decision == 'deny':
        access_request.status = 'denied'

    access_request.save()
    collection.save()
    return redirect('cla:manageAccessRequests')

def handleItemRequestDecision(request, request_id, decision):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    access_request = get_object_or_404(ItemAccessRequest, id=request_id)

    if decision == 'approve':
        access_request.status = 'approved'
        access_request.item.status = 'unavailable'
        access_request.item.save()

        Notification.objects.create(
            user=access_request.patron,
            message=f"Your request for '{access_request.item.title}' has been approved! Please pick it up."
        )

        patron = access_request.patron
        item = access_request.item
        item.borrower = patron
        item.borrowed_at = timezone.now()
        item.due_date = timezone.now() + timedelta(days=30)
        item.save()

    elif decision == 'deny':
        access_request.status = 'denied'

        Notification.objects.create(
            user=access_request.patron,
            message=f"Your request for '{access_request.item.title}' has been denied."
        )

    access_request.save()
    return redirect('cla:manageAccessRequests')

def handleAccessItemPatron(request, item_id):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:librarianSearch')
    except:
        return redirect('cla:index')

    # https://docs.djangoproject.com/en/5.2/ref/request-response/
    # https://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python
    # using json for ease in transferring information, as this is a helper function and not actually sending a view
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method.'}, status=400)

    item = get_object_or_404(LibrarianItem, id=item_id)

    if ItemAccessRequest.objects.filter(patron=request.user, item=item, status='pending').exists():
        return JsonResponse({'message': 'You\'ve already requested this item.'}, status=400)

    #change to available
    if item.status != 'available':
        return JsonResponse({'message': 'Item is currently not available.'}, status=400)

    ItemAccessRequest.objects.create(patron=request.user, item=item)
    return JsonResponse({'message': 'Your request has been submitted.'}, status=200)

def patronNotifications(request):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:librarianSearch')
    except:
        return redirect('cla:index')

    borrowed_items = LibrarianItem.objects.filter(borrower=user)
    pending_requests = ItemAccessRequest.objects.filter(patron=user, status='pending')
    notifications = Notification.objects.filter(user=user).order_by('-created_at')
    Notification.objects.filter(user=user).update(is_read=True)

    return render(request, 'cla/patronNotifications.html', {
        'borrowed_items': borrowed_items,
        'pending_requests': pending_requests,
        'notifications': notifications,
    })


def clear_all_notifications(request):
    user = request.user

    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:librarianSearch')
    except:
        return redirect('cla:index')

    Notification.objects.filter(user=user).delete()
    return redirect('cla:patronNotifications')


def patronItemsBorrowed(request):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:librarianSearch')
    except:
        return redirect('cla:index')

    borrowed_items = LibrarianItem.objects.filter(borrower=user)

    return render(request, 'cla/itemsBorrowedPatron.html', {
        'borrowed_items': borrowed_items,
    })


def returnItemRequest(request, item_id):
    ### Patron Function ###
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method.'}, status=400)
    
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if user_type.is_librarian:
            return redirect('cla:librarianSearch')
    except:
        return redirect('cla:index')

    item = get_object_or_404(LibrarianItem, id=item_id)

    # https://docs.djangoproject.com/en/5.2/ref/request-response/
    # https://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python
    # using json for ease in transferring information, as this is a helper function and not actually sending a view
    if ItemReturnRequest.objects.filter(patron=user, item=item, status='pending').exists():
        return JsonResponse({'message': 'You\'ve already requested to return this item.'}, status=400)
    
    ItemReturnRequest.objects.create(patron=user, item=item)
    return JsonResponse({'message': 'Your return request has been submitted.'}, status=200)


def handleReturnRequest(request, request_id, decision):
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    return_request = get_object_or_404(ItemReturnRequest, id=request_id)
    
    if decision == 'received':
        return_request.status = 'received'
        return_request.item.status = 'available'
        return_request.item.borrower = None
        return_request.item.borrowed_at = None
        return_request.item.due_date = None
        return_request.item.save()
        return_request.save()

        Notification.objects.create(
            user=return_request.patron,
            message=f'Your returned item "{return_request.item.title}" has been received by the librarian!'
        )
    elif decision == 'not_received':
        Notification.objects.create(
            user=return_request.patron,
            message=f'Your returned item "{return_request.item.title}" has not been properly returned. Return request denied.'
        )
        return_request.delete()
    return redirect('cla:manageAccessRequests')

# Function for patrons to request for a librarian to upgrade their account to a librarian
def upgradeAccountRequest(request):
    if request.method != "POST":
        return JsonResponse({'error': 'Invalid request method. Please try again.'}, status=400)
    
    user = request.user

    # https://docs.djangoproject.com/en/5.2/ref/request-response/
    # https://stackoverflow.com/questions/2428092/creating-a-json-response-using-django-and-python
    # using json for ease in transferring information, as this is a helper function and not actually sending a view
    if AccountUpgradeRequest.objects.filter(patron=request.user, status='pending').exists():
        return JsonResponse({'message': 'Request already sent.'}, status=400)

    upgrade_request = AccountUpgradeRequest.objects.create(patron=request.user)
    return JsonResponse({'message': 'Request to upgrade account to librarian submitted.'}, status=200)

# librarian's side: handles approve or deny to a patron's upgrade request
def handleUpgradeAccountRequest(request, request_id, decision):
    upgrade_request = get_object_or_404(AccountUpgradeRequest, id=request_id)
    if decision == 'approve':
        upgrade_request.status = 'approved'
        user = upgrade_request.patron
        user_email = user.email
        user_type = UserType.objects.get(email=user_email)
        user_type.is_librarian = True
        user_type.save()
    
    elif decision == 'deny':
        upgrade_request.status = 'denied'
        Notification.objects.create(
            user=upgrade_request.patron,
            message=f"Your request to become a librarian has been denied."
        )
    upgrade_request.save()
    return redirect('cla:manageAccessRequests')

def viewMyItems(request):
    template_name = "cla/viewMyItems.html"
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    my_items = LibrarianItem.objects.filter(owner=user)
    context = {
        'user': user,
        'items': my_items,
    }
    return render(request, template_name, context)

def viewMyGames(request):
    template_name = "cla/viewMyGames.html"
    user = request.user

    # If anonymous user
    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        # If librarian
        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    my_games = LibrarianItem.objects.filter(owner=user)
    context = {
        'user': user,
        'my_games': my_games,
    }
    return render(request, 'cla/viewMyGames.html', context)


def signup(request):
    template_name = "cla/signup.html"
    return render(request, 'cla/signup.html')


class CustomLogoutView(LogoutView):
    def dispatch(self, request, *args, **kwargs):
        list(messages.get_messages(request))    # clears all messages
        return super().dispatch(request, *args, **kwargs)


class signupLibrarian(generic.CreateView):
    model = UserType
    form_class = LibrarianSignUpForm
    template_name = "cla/signupLibrarian.html"
   
    def post(self, request):
        form = LibrarianSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cla:loginLibrarian')
        return render(request, 'cla/signupLibrarian.html', {'form': form})

class signupPatron(generic.CreateView):
    model = UserType
    form_class = PatronSignUpForm
    template_name = "cla/signupPatron.html"

    def post(self, request):
        form = PatronSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('cla:loginPatron')
        else:
            return render(request, 'cla/signupPatron.html', {'form': form})


#Redirects users based on whether they are patrons or librarians
@login_required
def login_success(request):    
    user = request.user #the user
    userGmail = user.email #their email

    userAccount = get_user_by_email(userGmail)

    # if the user has signed up for an account
    if userAccount:
        #print(userAccount.is_librarian)
        if(userAccount.is_librarian):
            #librarians:upload
            return redirect('cla:librarianSearch')
        else:
            return redirect('cla:patronSearch')
    else:
        return redirect('cla:signup')


def get_user_by_email(email):
    try:
        return UserType.objects.get(email=email)
    except UserType.DoesNotExist:
        return None


@login_required
def patronProfile(request):
    user = request.user
    user_account = get_user_account(request)
    date_joined = user.date_joined
    is_librarian: bool = user_account.is_librarian
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, 
                                   request.FILES, 
                                   instance=user.profile)
        if p_form.is_valid():
            p_form.save()
            messages.success(request, 'Your icon has been updated')
            return redirect('cla:patronProfile')
    else:
        p_form = ProfileUpdateForm(instance=user.profile)
        
    template_name = "cla/patronProfile.html"
    context = {
        'p_form': p_form,
        'date_joined': date_joined,
        'is_librarian': is_librarian
    }
    return render(request, template_name, context)

@login_required
def account_redirect(request):
    '''
    Source: ChatGPT 4o
    Prompt: How to achieve dynamic redirects in Django Google Auth by altering HTML links
    '''

    redirect_url = request.GET.get('next')
    return redirect(redirect_url)
