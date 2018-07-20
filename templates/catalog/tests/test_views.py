from django.test import TestCase

from django.core.urlresolvers import reverse

import datetime
from django.utils import timezone
from catalog.models import Author, BookInstance, Book, Genre, Language
from django.contrib.auth.models import User

from django.contrib.auth.models import Permission # required to grant permission needed to set a book as returned

class AuthorListViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        #create 13 authors for pagination tests
        number_of_authors = 13
        for author_num in range(number_of_authors):
            Author.objects.create(first_name='Faisal %s' % author_num, last_name = 'Surname %s' % author_num,)

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/catalog/authors/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('catalog:authors'))
        self.assertEqual(resp.status_code, 200)
        
    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('catalog:authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'catalog/author_list.html')

    def test_pagination_is_ten(self):
        resp = self.client.get(reverse('catalog:authors'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['author_list']) == 10)

    def test_lists_all_authors(self):
        #Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('catalog:authors')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['author_list']) == 3)

class LoanedBookInstancesByUserListViewTest(TestCase):

    def setUp(self):
        #create two users
        test_user1 = User.objects.create_user(username='testuser1', password='1234')
        test_user1.save() 
        test_user2 = User.objects.create_user(username='testuser2', password='1234')
        test_user2.save()

        #create a book
        test_author = Author.objects.create(first_name='faisal', last_name='seif')
        test_genre = Genre.objects.create(name='Fantacy')
        test_language = Language.objects.create(name='English')
        test_book = Book.objects.create(title='Book Title', summary='My book summary', isbn='ABSCED', author='test_author', language='test_language')
        
        #create genre as a post step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) #Direct assignment for many to many fields types not allowed
        test_book.save()

        #create 30 BookInstance objects
        number_of_book_copies = 30
        for book_copy in range(number_of_book_copies):
            return_date = timezone.now() + datetime.timedelta(days=book_copy%5)
            if book_copy % 2:
                the_borrower = test_user1
            else:
                the_borrower = test_user2
        BookInstance.objects.create(book=test_book, imprint='Unlikely imprint, 2016', due_back=return_date, borrower=the_borrower, status=status)

        def test_redirect_if_not_logged_in(self):
            resp = self.client.get(reverse('catalog:my-borrowed'))
            self.assertRedirects(resp, '/accounts/login/?next=/catalog/mybooks')

        def test_logged_in_uses_correct_template(self):
            login = self.client.login(username='test_user1', password='1234')
            resp = self.client.get(reverse('catalog:my-borrowed'))
            # check our user is logged in
            self.assertEqual(str(resp.context['user']), 'test_user1')
            # check that we got a response "success"
            self.assertEqual(resp.status_code, 200)
            # check we used correct template
            self.assertTemplateUsed(resp, 'catalog/bookinstance_list_borrowed_user.html')

        def test_only_borrowed_books_in_list(self):
            login = self.client.login(username='test_user1', password='1234')
            resp = self.client.get(reverse('catalog:my-borrowed'))

            #check our user is logged in
            self.assertEqual(str(resp.context['user']), 'test_user1')
            #chcek that we got a response "success"
            self.assertEqual(resp.status.code, 200)

            #check that we initialy there is no book in list(none on loan)
            self.assertTrue('bookinstance_list' in resp.context)
            self.assertEqual(len(resp.context['bookinstance_list']), 0)

            #Now change all books to be on loan
            get_ten_books = BookInstance.objects.all()[:10]

            for copy in get_ten_books:
                copy.status = 'o'
                copy.save()

            #check that we have borrowed books in the list
            resp = self.client(reverse('catalog:my-borrowed'))
            # check that the user is logged in
            self.assertEqual(str(resp.context['user']), 'test_user1')
            #check the status response "success"
            self.assertEqual(resp.status.code, 200)

        def test_pages_ordered_by_due_date(self):

            #change all books to be on loan
            for copy in BookInstance.objects.all():
                copy.status='o'
                copy.save()

            login = self.client.login(username='test_user1', password='1234')
            resp = self.client.get(reverse('catalog:my-borrowed'))

            #check if user is logged in
            self.assertEqual(str(resp.context['user']), 'test_user1')
            #check if the status response is "success"
            self.assertEqual(resp.status.code, 200)

            #confirm that of the items, only ten are displayed due to pagination
            self.assertEqual(len(resp.context['bookinstance_list']), 10)
            last_date=0
            for copy in resp.context['bookinstance_list']:
                if last_date == 0:
                    last_date=copy.due_back
                else:
                    self.assertTrue(last_date <= copy.due_back)
        

class RenewBookInstancesViewTest(TestCase):

    def setUp(self):
        #create a user
        test_user1 = User.objects.create_user(username='testuser1', password='12345')
        test_user1.save()
        
        test_user2 = User.objects.create_user(username='testuser2', password='12345')
        test_user2.save()
        permission = Permission.objects.get(name='Set book as returned')
        test_user2.user_permissions.add(permission)

        #create a book
        test_author = Author.objects.create(first_name='john', last_name='Smith')
        test_genre = Genre.objects.create(name='Fantacy')
        test_language = Language.objects.create(language_name='English')
        test_book = Book.objects.create(title='Book title', summary='My Book Summary', isbn='ABCEDEF', author=test_author, language=test_language)
 
        #create a genre as a post step
        genre_objects_for_book = Genre.objects.all()
        test_book.genre.set(genre_objects_for_book) # Direct assignment of many to  many types not allowed
        test_book.save()

        #create a BookInstance object for test_user1
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance1 = BookInstance.objects.create(book=test_book, imprint='Unlikely, 2016', due_back=return_date, borrower=test_user1, status='o')
 
        #create a BookInstance object for test_user2
        return_date = datetime.date.today() + datetime.timedelta(days=5)
        self.test_bookinstance2 = BookInstance.objects.create(book=test_book, imprint='Unlikely, 2016', due_back=return_date, borrower=test_user2, status='o')

    def test_redirect_if_not_logged_in(self):
        resp = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id': self.test_bookinstance1.pk,}))
        #Manually check redirect (Can't user assertRedirect, because the redirect URL is unpredictable)
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(resp.url.startswith('/accounts/login/'))
    
    def test_redirect_if_logged_in_but_not_correct_permission(self):
        login = self.client.login(username='testuser1', password='12345')
        resp = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id':self.test_bookinstance1.pk,}) )

        #Manually check redirects ( Cant use assertRedirect because URL is unpredictable)
        self.assertEqual( resp.status_code, 302)
        self.assertTrue( resp.url.startswith('/accounts/login/'))

    def test_logged_in_with_permission_borrowed_book(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id':self.test_bookinstance2.pk,}) )

        #check that it lets us login - this is our book and we have the right permissions
        self.assertEqual(resp.status_code, 200)
    
    def test_logged_in_with_permission_another_users_borrowed_book(self):

        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id':self.test_bookinstance1.pk,}) )

        #check that it lets us login - We are librarian, so we can view any users book
        self.assertEqual(resp.status_code, 200) 

    def test_HTTP404_for_invalid_book_if_logged_in(self):
        import uuid
        test_uid = uuid.uuid4() #unlikely UID to match our bookinstance!
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id':test_uid,}) )
        self.assertEqual(resp.status_code, 404)

    def test_uses_correct_template(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id':self.test_bookinstance1.pk,}) )
        self.assertEqual(resp.status_code, 200)

        #check we used correct template
        self.assertTemplateUsed(resp, 'catalog/book_renew_librarian.html')

    def test_form_renewal_date_initially_has_date_three_weeks_in_future(self):
        login = self.client.login(username='testuser2', password='12345')
        resp = self.client.get(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id':self.test_bookinstance1.pk,}) )
        self.assertEqual(resp.status_code, 200)

        date_3_weeks_in_future = datetime.date.today() + datetime.timedelta(weeks=3)
        self.assertEqual(resp.context['form'].initial['renewal_date'], date_3_weeks_in_future)

    def test_redirects_to_all_borrowed_book_list_on_success(self):
        login = self.client.login(username='testuser2', password='12345')
        valid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=2)
        resp = self.client.post(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id':self.test_bookinstance1.pk,}), {'renewal_date': valid_date_in_future} )
        self.assertRedirects(resp, reverse('catalog:all-borrowed'))

    def test_form_invalid_renewal_date_past(self):
        login = self.client.login(username='testuser2', password='12345')
        date_in_past = datetime.date.today() - datetime.timedelta(weeks=1)
        resp = self.client.post(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id': self.test_bookinstance1.pk,}), {'renewal_date': date_in_past} )
        self.assertEqual(resp.status_code, 200)
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal in past')

    def test_form_invalid_renewal_date_future(self):
        login = self.client.login(username='testuser2', password='12345')
        invalid_date_in_future = datetime.date.today() + datetime.timedelta(weeks=5)
        resp = self.client.post(reverse('catalog:renew-book-librarian', kwargs={'bookinst_id': self.test_bookinstance1.pk,}), {'renewal_date': invalid_date_in_future} )
        self.assertEqual(resp.status_code, 200 )
        self.assertFormError(resp, 'form', 'renewal_date', 'Invalid date - renewal more than 4 weeks old')
