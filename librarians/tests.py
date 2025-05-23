from django.test import TestCase
from django.urls import reverse
from .models import LibrarianItem, User
from cla.models import UserType


# Create your tests here.
class LibrarianViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='test',
            email='test@test.com',
            password='test1234'
        )

        self.user_type = UserType.objects.create(
            email='test@test.com',
            is_librarian=True
        )

    def test_view_items_page_load(self):
        self.client.login(username='test', password='test1234')

        response = self.client.get(reverse('librarians:view_items'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'librarians/view_items.html')
    
    def test_upload_item_page_load(self):
        self.client.login(username='test', password='test1234')

        response = self.client.get(reverse('librarians:upload'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'librarians/upload.html')
    
    def test_upload_item_form(self):
        self.client.login(username='test', password='test1234')

        payload = {     # create raw POST request payload instead of Form object (best for unit tests)
            'title': 'Board Game A',
            'status': 'available',
            'location': 'Charlottesville, VA',
            'description': 'Best Game Ever',
            'tags': 'a'
        }
        response = self.client.post(reverse('librarians:upload'), data=payload)

        # Test redirect
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('librarians:upload'))
        self.assertTrue(LibrarianItem.objects.exists())

        # Test database persistence
        librarianItem = LibrarianItem.objects.first()
        self.assertEqual(librarianItem.title, 'Board Game A')
        self.assertEqual(librarianItem.status, 'available')
        self.assertEqual(librarianItem.location, 'Charlottesville, VA')
        self.assertEqual(librarianItem.description, 'Best Game Ever')
