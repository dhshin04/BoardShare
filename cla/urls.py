from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = "cla"

# https://stackoverflow.com/questions/58180922/how-do-i-properly-use-a-uuid-id-as-a-url-parameter-in-django
# help with perserving context and sending in urls
urlpatterns = [
    path("", views.index, name="index"),
    path("signup/", views.signup, name="signup"),
    path("signupPatron/", views.signupPatron.as_view(), name="signupPatron"),
    path("signupLibrarian/", views.signupLibrarian.as_view(), name="signupLibrarian"),
    path("login/", views.login, name="login"),
    path("loginPatron/", views.loginPatron, name="loginPatron"),
    path("loginLibrarian/", views.loginLibrarian, name="loginLibrarian"),
    path("register/", views.register, name="register"),
    path('logout/', views.CustomLogoutView.as_view(next_page=''), name='logout'),
    path("librarianSearch/", views.librarianSearch, name="librarianSearch"),
    path("patronSearch/", views.patronSearch, name="patronSearch"),
    path("search/", views.search, name="search"),
    path("searchAnon/", views.searchAnon, name="searchAnon"),
    path("patronProfile/", views.patronProfile, name="patronProfile"),
    path("addCollection/", views.addCollection, name="addCollection"),
    path("itemDisplay/<uuid:item_id>/", views.itemDisplay, name="itemDisplay"),
    path("itemDisplayPatron/<uuid:item_id>/", views.itemDisplayPatron, name="itemDisplayPatron"),
    path("itemDisplayAnon/<uuid:item_id>/", views.itemDisplayAnon, name="itemDisplayAnon"),
    path("publicCollectionDisplay/<int:collection_id>/", views.publicCollectionDisplay, name="publicCollectionDisplay"),
    path("publicCollectionDisplayPatron/<int:collection_id>/", views.publicCollectionDisplayPatron, name="publicCollectionDisplayPatron"),
    path("publicCollectionDisplayAnon/<int:collection_id>/", views.publicCollectionDisplayAnon, name="publicCollectionDisplayAnon"),
    path("searchCollection/<int:collection_id>/", views.searchCollection, name="searchCollection"),
    path("searchCollectionAnon/<int:collection_id>/", views.searchCollectionAnon, name="searchCollectionAnon"),
    path("addCollectionPatron/", views.addCollectionPatron, name="addCollectionPatron"),
    path("viewCollectionsPatron/", views.viewCollectionsPatron, name="viewCollectionsPatron"),
    path("viewCollectionsLibrarian/", views.viewCollectionsLibrarian, name="viewCollectionsLibrarian"),
    path("addToCollection/", views.addToCollection, name="addToCollection"),
    path('addItemToCollection/<uuid:item_id>/', views.addItemToCollection, name='addItemToCollection'),
    path('addItemToCollectionSubmit/<uuid:item_id>/', views.addItemToCollectionSubmit, name='addItemToCollectionSubmit'),
    path('deleteItemFromCollection/<uuid:item_id>/', views.deleteItemFromCollection, name='deleteItemFromCollection'),
    path('deleteItemFromCollectionSubmit/<uuid:item_id>/', views.deleteItemFromCollectionSubmit, name='deleteItemFromCollectionSubmit'),
    path("viewMyItems/", views.viewMyItems, name="viewMyItems"),
    path("viewMyGames/", views.viewMyGames, name="viewMyGames"),
    path('requestAccess/<int:collection_id>/', views.requestAccess, name='requestAccess'),
    path('manageAccessRequests/', views.manageAccessRequests, name='manageAccessRequests'),
    path('handleAccessRequest/<int:request_id>/<str:decision>/', views.handleAccessRequest, name='handleAccessRequest'),
    path('collection/<int:collection_id>/', views.singleCollectionSearch, name='singleCollectionSearch'),
    path('requestItem/<uuid:item_id>/', views.handleAccessItemPatron, name='handleAccessItemPatron'),
    path('upgradeAccountRequest/', views.upgradeAccountRequest, name='upgradeAccountRequest'),
    path('handleUpgradeAccountRequest/<int:request_id>/<str:decision>/', views.handleUpgradeAccountRequest, name='handleUpgradeAccountRequest'),
    path('handleItemRequestDecision/<int:request_id>/<str:decision>/', views.handleItemRequestDecision, name='handleItemRequestDecision'),
    path('patronNotifications/', views.patronNotifications, name='patronNotifications'),
    path('anonymousSearch/', views.anonymousSearch, name='anonymousSearch'),
    path('patronItemsBorrowed/', views.patronItemsBorrowed, name='patronItemsBorrowed'),
    path('returnItemRequest/<uuid:item_id>/', views.returnItemRequest, name='returnItemRequest'),
    path('handleReturnRequest/<int:request_id>/<str:decision>/', views.handleReturnRequest, name='handleReturnRequest'),
    path('editItem/<uuid:item_id>/', views.editItem, name='editItem'),
    path('editItemSubmit/<uuid:item_id>/', views.editItemSubmit, name='editItemSubmit'),
    path('deleteItem/<uuid:item_id>/', views.deleteItem, name='deleteItem'),
    path('deleteItemSubmit/<uuid:item_id>/', views.deleteItemSubmit, name='deleteItemSubmit'),
    path('editCollection/<int:collection_id>/', views.editCollection, name='editCollection'),
    path('editCollectionSubmit/<int:collection_id>/', views.editCollectionSubmit, name='editCollectionSubmit'),
    path('deleteCollection/<int:collection_id>/', views.deleteCollection, name='deleteCollection'),
    path('deleteCollectionSubmit/<int:collection_id>/', views.deleteCollectionSubmit, name='deleteCollectionSubmit'),
    path('clear_all_notifications', views.clear_all_notifications, name='clear_all_notifications')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
