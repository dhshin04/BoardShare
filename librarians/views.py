from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LibrarianItemsForm, LibrarianItemsImageForm, CollectionsForm
from .models import LibrarianItem, LibrarianItemImage
from cla.models import UserType


def upload_item(request):
    user = request.user

    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    if request.method == 'POST':
        librarian_form = LibrarianItemsForm(request.POST)
        librarian_image_form = LibrarianItemsImageForm(request.POST, request.FILES)
        if librarian_form.is_valid() and librarian_image_form.is_valid():
            librarian = librarian_form.save(commit=False)
            librarian.owner = request.user if request.user.is_authenticated else None
            librarian.save()
            # for taggit
            librarian_form.save_m2m()

            image = librarian_image_form.save(commit=False)
            uploaded = librarian_image_form.cleaned_data.get('image')
            if uploaded:
                image = LibrarianItemImage(item=librarian, image=uploaded)
                image.save()

            messages.success(request, 'Item uploaded successfully')     # Flashes success messages
            return redirect('librarians:upload')
        else:
            messages.error(request, 'Item failed to upload')
            return redirect('librarians:upload')
    else:
        librarian_form = LibrarianItemsForm()
        librarian_image_form = LibrarianItemsImageForm(request.POST, request.FILES)

    return render(request, 'librarians/upload.html', {'form': librarian_form, 'image_form': librarian_image_form})

def view_items(request):
    user = request.user

    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    items = LibrarianItem.objects.all()
    return render(request, 'librarians/view_items.html', {'items': items})

def create_collections(request):
    user = request.user

    if user.is_anonymous:
        return redirect('cla:index')
    
    try:
        user_type = UserType.objects.filter(email=user.email).first()

        if not user_type:
            return redirect('cla:index')
        if not user_type.is_librarian:
            return redirect('cla:patronSearch')
    except:
        return redirect('cla:index')

    if request.method == 'POST':
        collection_form = CollectionsForm(request.POST)
        if collection_form.is_valid():
            collection = collection_form.save(commit=False)
            collection.owner = request.user
            collection.save()
            messages.success(request, 'Collection created successfully')
            return redirect('librarians:collection')
    else:
        collection_form = CollectionsForm()

    return render(request, 'librarians/collection.html', {'form': collection_form})
