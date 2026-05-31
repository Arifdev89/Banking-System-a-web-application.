from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from decimal import Decimal
from .models import Account, Transaction


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'banking/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken.')
            return render(request, 'banking/register.html')

        user = User.objects.create_user(username=username, email=email, password=password)
        Account.objects.create(user=user)
        messages.success(request, 'Account created! Please login.')
        return redirect('login')

    return render(request, 'banking/register.html')


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid credentials.')
    return render(request, 'banking/login.html')


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def dashboard_view(request):
    account = Account.objects.get(user=request.user)
    transactions = account.transactions.all()[:10]
    return render(request, 'banking/dashboard.html', {
        'account': account,
        'transactions': transactions,
    })


@login_required
def deposit_view(request):
    account = Account.objects.get(user=request.user)
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        if amount <= 0:
            messages.error(request, 'Enter a valid amount.')
        else:
            with transaction.atomic():
                account.balance += amount
                account.save()
                Transaction.objects.create(
                    account=account,
                    transaction_type='DEPOSIT',
                    amount=amount,
                    balance_after=account.balance,
                    description='Cash Deposit'
                )
            messages.success(request, f'₹{amount} deposited successfully!')
            return redirect('dashboard')
    return render(request, 'banking/deposit.html', {'account': account})


@login_required
def withdraw_view(request):
    account = Account.objects.get(user=request.user)
    if request.method == 'POST':
        amount = Decimal(request.POST.get('amount', 0))
        if amount <= 0:
            messages.error(request, 'Enter a valid amount.')
        elif amount > account.balance:
            messages.error(request, 'Insufficient balance.')
        else:
            with transaction.atomic():
                account.balance -= amount
                account.save()
                Transaction.objects.create(
                    account=account,
                    transaction_type='WITHDRAW',
                    amount=amount,
                    balance_after=account.balance,
                    description='Cash Withdrawal'
                )
            messages.success(request, f'₹{amount} withdrawn successfully!')
            return redirect('dashboard')
    return render(request, 'banking/withdraw.html', {'account': account})


@login_required
def transfer_view(request):
    account = Account.objects.get(user=request.user)
    if request.method == 'POST':
        to_acc_number = request.POST.get('account_number')
        amount = Decimal(request.POST.get('amount', 0))

        if amount <= 0:
            messages.error(request, 'Enter a valid amount.')
        elif amount > account.balance:
            messages.error(request, 'Insufficient balance.')
        else:
            try:
                to_account = Account.objects.get(account_number=to_acc_number)
                if to_account == account:
                    messages.error(request, 'Cannot transfer to your own account.')
                else:
                    with transaction.atomic():
                        account.balance -= amount
                        account.save()
                        to_account.balance += amount
                        to_account.save()
                        Transaction.objects.create(
                            account=account,
                            transaction_type='TRANSFER_OUT',
                            amount=amount,
                            balance_after=account.balance,
                            description=f'Transfer to {to_account.user.username}'
                        )
                        Transaction.objects.create(
                            account=to_account,
                            transaction_type='TRANSFER_IN',
                            amount=amount,
                            balance_after=to_account.balance,
                            description=f'Transfer from {account.user.username}'
                        )
                    messages.success(request, f'₹{amount} transferred successfully!')
                    return redirect('dashboard')
            except Account.DoesNotExist:
                messages.error(request, 'Account number not found.')

    return render(request, 'banking/transfer.html', {'account': account})


@login_required
def transactions_view(request):
    account = Account.objects.get(user=request.user)
    transactions = account.transactions.all()
    return render(request, 'banking/transactions.html', {
        'account': account,
        'transactions': transactions,
    })
