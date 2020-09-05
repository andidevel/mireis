from django.urls import path

from . import views

app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('register', views.register, name='register'),
    path('login', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('journal', views.journal, name='journal'),
    path('account-list', views.account_list, name='account-list'),
    path('add-account', views.add_account, name='add-account'),
    path('edit-account/<int:pk>', views.edit_account, name='edit-account'),
    path('save-account', views.save_account, name='save-account-add'),
    path('save-account/<int:pk>', views.save_account, name='save-account-edit'),
    path('del-account/<int:pk>', views.del_account, name='del-account'),
    path('transaction/<int:pk>', views.get_transaction, name='transaction'),
    path('save-transaction', views.save_transaction, name='save-transaction-add'),
    path('save-transaction/<int:pk>', views.save_transaction, name='save-transaction-edit'),
]