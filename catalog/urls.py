
from django.conf.urls import url
from . import views

app_name = 'catalog'
urlpatterns = [
     url(r'^$', views.index, name='index'),
     url(r'^books/', views.BookListView.as_view(), name='books'),
     url(r'^book/(?P<pk>[0-9]+)$', views.BookDetailView.as_view(), name='book-detail'),
     url(r'^authors/', views.AuthorListView.as_view(), name='authors'),
     url(r'^author/(?P<pk>[0-9]+)$', views.AuthorDetailView.as_view(), name='author-detail'),
]

urlpatterns += [
     url(r'^mybooks/', views.LoanedBooksByUserListView.as_view(), name='my-borrowed'),
     url(r'^borrowed/', views.LoanedBooksAllListView.as_view(), name='all-borrowed'),
] 

urlpatterns += [
     url(r'^book/(?P<bookinst_id>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/renew/$', views.renew_book_librarian, name='renew-book-librarian'),
]

urlpatterns += [
     url(r'^author/create/', views.AuthorCreate.as_view(), name='author_create'),
     url(r'^author/(?P<pk>[0-9]+)/update/$', views.AuthorUpdate.as_view(), name='author_update'),
     url(r'^author/(?P<pk>[0-9]+)/delete/$', views.AuthorDelete.as_view(), name='author_delete'),
]

urlpatterns += [
     url(r'^book/create/', views.BookCreate.as_view(), name='book_create'),
     url(r'^book/(?P<pk>[0-9]+)/update/$', views.BookUpdate.as_view(), name='book_update'),
     url(r'^book/(?P<pk>[0-9]+)/delete/$', views.BookDelete.as_view(), name='book_delete'),
]
