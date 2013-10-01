from django.db import models, transaction
from django.contrib.auth.models import User
from idlebook.account.models import Trade

class TransactionManager(models.Manager):
    
    # 11
    @transaction.commit_on_success
    def deposit(self, user, trade, amount):
        transaction = self.create(
            trade=trade,
            buyer=user,
            status=1,
            type=1,
            method=1,
            buyer_balance=user.wallet.regular_balance+amount,
            buyer_deposit=user.wallet.reserved_balance,
            earning=amount,
        )
        user.wallet.deposit(amount, 'regular')
        IdlebookAccount.objects.user_deposit(transaction, amount)


    # 23
    @transaction.commit_on_success
    def withdraw(self, user, amount):
        transaction = self.create(
            buyer=user,
            status=1,
            type=2,
            method=3,
            buyer_balance=user.wallet.regular_balance-amount,
            buyer_deposit=user.wallet.reserved_balance,
            payment=amount
        )
        user.wallet.withdraw(amount, 'regular')
        IdlebookAccount.objects.user_withdraw(transaction, amount)


    #30
    @transaction.commit_on_success
    def return_deposit(self, user, trade):
        amount = trade.lease.deposit
        if amount > 0:
            transaction = self.create(
                trade=trade,
                buyer=user,
                status=1,
                type=3,
                method=0,
                buyer_balance=user.wallet.regular_balance+amount,
                buyer_deposit=user.wallet.reserved_balance-amount,
                deposit=-amount,
            )
            user.wallet.unread = True
            user.wallet.save()
            user.wallet.withdraw(amount, 'reserved')
            user.wallet.deposit(amount, 'regular')
            trade.lease.deposit = 0
            trade.lease.save()


    # 00 for buyer, 01
    @transaction.commit_on_success    
    def transfer(self, buyer, seller, trade, price, earning, deposit):
        transaction = self.create(
            trade=trade,
            seller=seller,
            buyer=buyer,
            status=1,
            type=0,
            method=0,
            seller_balance=seller.wallet.regular_balance+earning,
            buyer_balance=buyer.wallet.regular_balance-price-deposit,
            buyer_deposit=buyer.wallet.reserved_balance+deposit,
            payment=price,
            earning=earning,
            deposit=deposit,
        )
        seller.wallet.unread = True
        seller.wallet.save()
        buyer.wallet.hold(price + deposit)
        seller.wallet.deposit(earning, 'regular')
        buyer.wallet.deposit(deposit, 'reserved')
        buyer.wallet.flush_hold()
        IdlebookAccount.objects.user_trade(transaction, price-earning)


class Transaction(models.Model):
    """
    table for all transactions
    
    """
    
    # many to one
    trade           = models.ForeignKey(Trade, related_name='transactions', null=True)
    buyer           = models.ForeignKey(User, related_name='transactions', null=True)
    seller          = models.ForeignKey(User, related_name='incomes', null=True)
    
    # fields    
    add_time        = models.DateTimeField(auto_now_add=True)   # time this transaction is made
    update_time     = models.DateTimeField(auto_now=True)   # time this is transaction is updated
    status          = models.SmallIntegerField(default=0)   # status of the transaction, either pending 0, auhorized 1, or declined 2
    type            = models.SmallIntegerField(default=0)   # type. transfer 0, deposit 1, cash out 2,  return deposit 3
    method          = models.SmallIntegerField(default=0)   # payment method. transfer 0, square 1, chase 2, check 3, cash 4
    buyer_balance   = models.IntegerField(null=True)    # buyer's balance after transaction
    buyer_deposit   = models.IntegerField(null=True)    # buyer's deposit amount after transaction
    seller_balance  = models.IntegerField(null=True)    # seller's balance after transaction
    
    payment         = models.IntegerField(default=0)    # buyer's total payment
    earning         = models.IntegerField(default=0)    # seller's earning
    deposit         = models.IntegerField(default=0)    # deposit amount possible = deposit, negative = withdraw
    fee             = models.IntegerField(default=0)    # fee for the payment method, give to square or chase


    objects = TransactionManager()


class IdlebookAccountManager(models.Manager):

    def get_balance(self):
        rows = self.order_by('-add_time')
        if rows.exists():
            return rows[0].balance
        else:
            return 0

    def get_revenue(self):
        rows = self.order_by('-add_time')
        if rows.exists():
            return rows[0].revenue
        else:
            return 0

    def user_deposit(self, transaction, amount):
        self.create(
            transaction=transaction,
            amount=amount,
            balance=self.get_balance()+amount,
            revenue=self.get_revenue()
        )

    def user_withdraw(self, transaction, amount):
        self.create(
            transaction=transaction,
            amount=-amount,
            balance=self.get_balance()-amount,
            revenue=self.get_revenue()
        )
        
    def user_trade(self, transaction, commission):
        self.create(
            transaction=transaction,
            commission=commission,
            balance=self.get_balance(),
            revenue=self.get_revenue()+commission
        )



class IdlebookAccount(models.Model):
    """
    it's Idlebook's account that adds a new row everytime people makes a payment
    """

    # this transaction
    transaction = models.ForeignKey(Transaction, related_name='idlebook')
    # total amount per transaction
    amount      = models.IntegerField(default=0)
    # revenue we make per transaction
    commission  = models.IntegerField(default=0)
    # total revenue (amount of money we take)
    revenue     = models.IntegerField(null=True)
    # total balance (all amount, include ones to return)
    balance     = models.IntegerField(null=True)
    # time this row get added
    add_time    = models.DateTimeField(auto_now_add=True)


    objects = IdlebookAccountManager()


    def __unicode__(self):
        return "%s %s" % (self.revenue, self.balance)

