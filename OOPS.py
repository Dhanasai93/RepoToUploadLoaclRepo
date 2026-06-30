"""
OOP Concepts in Python — demonstrated through a Banking System
=================================================================
Covers: Class & Object, Encapsulation, Inheritance, Polymorphism,
        Abstraction, Constructors, Class/Static methods, Dunder methods.
"""

from abc import ABC, abstractmethod
from datetime import datetime


# -------------------------------------------------------------------
# 1. ABSTRACTION
# Abstract base class defines a contract that every account type
# MUST follow, without specifying how each one implements it.
# -------------------------------------------------------------------
class Account(ABC):

    bank_name = "Lilly National Bank"          # class attribute (shared by all)
    _total_accounts = 0                        # class attribute used for tracking

    def __init__(self, account_holder, balance=0):
        # 2. ENCAPSULATION
        # Double underscore -> name-mangled "private" attribute.
        # Cannot be accessed directly as obj.__balance from outside.
        self.account_holder = account_holder
        self.__balance = balance
        self.__account_number = self._generate_account_number()
        self.transaction_history = []

        Account._total_accounts += 1

    # ---- Encapsulation: controlled access via getter/setter ----
    @property
    def balance(self):
        """Read-only access to balance (no direct write allowed)."""
        return self.__balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("Balance cannot be negative.")
        self.__balance = value

    def _set_balance_allow_overdraft(self, value):
        """Protected helper: lets subclasses like CurrentAccount go negative
        (within their own overdraft rules) without weakening the public setter."""
        self.__balance = value

    def _generate_account_number(self):
        # protected method (single underscore convention)
        return f"LNB{Account._total_accounts + 1000}"

    @property
    def account_number(self):
        return self.__account_number

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive.")
        self.__balance += amount
        self._log_transaction(f"Deposited ₹{amount}")
        return self.__balance

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive.")
        if amount > self.__balance:
            raise ValueError("Insufficient balance.")
        self.__balance -= amount
        self._log_transaction(f"Withdrew ₹{amount}")
        return self.__balance

    def _log_transaction(self, description):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.transaction_history.append(f"[{timestamp}] {description}")

    # ---- Abstraction: every subclass MUST implement this ----
    @abstractmethod
    def calculate_interest(self):
        """Each account type calculates interest differently."""
        pass

    # ---- Class method: operates on the class, not an instance ----
    @classmethod
    def get_total_accounts(cls):
        return cls._total_accounts

    # ---- Static method: utility function, no access to self/cls state ----
    @staticmethod
    def is_valid_amount(amount):
        return isinstance(amount, (int, float)) and amount > 0

    # ---- Dunder (magic) methods ----
    def __str__(self):
        return (f"{self.__class__.__name__} | {self.account_holder} | "
                f"A/C: {self.__account_number} | Balance: ₹{self.__balance:.2f}")

    def __repr__(self):
        return f"<{self.__class__.__name__} acc_no={self.__account_number}>"

    def __eq__(self, other):
        if not isinstance(other, Account):
            return False
        return self.account_number == other.account_number

    def __add__(self, other):
        """Allows acc1 + acc2 -> combined balance (just for demonstration)."""
        if isinstance(other, Account):
            return self.balance + other.balance
        return NotImplemented


# -------------------------------------------------------------------
# 3. INHERITANCE
# SavingsAccount and CurrentAccount inherit common behaviour from
# Account, but specialise calculate_interest() and add their own rules.
# -------------------------------------------------------------------
class SavingsAccount(Account):

    INTEREST_RATE = 0.04          # 4% annual interest
    MIN_BALANCE = 500

    def __init__(self, account_holder, balance=0):
        super().__init__(account_holder, balance)   # call parent constructor

    def withdraw(self, amount):
        # 4. POLYMORPHISM (method overriding)
        # Savings account enforces a minimum balance rule that the
        # base Account class does not know about.
        if self.balance - amount < self.MIN_BALANCE:
            raise ValueError(
                f"Withdrawal denied: minimum balance of ₹{self.MIN_BALANCE} must be maintained."
            )
        return super().withdraw(amount)

    def calculate_interest(self):
        interest = self.balance * self.INTEREST_RATE
        self._log_transaction(f"Interest credited ₹{interest:.2f}")
        self.deposit(interest)
        return interest


class CurrentAccount(Account):

    OVERDRAFT_LIMIT = 10000

    def __init__(self, account_holder, balance=0):
        super().__init__(account_holder, balance)

    def withdraw(self, amount):
        # Polymorphism: current accounts allow overdraft, savings don't.
        if amount > self.balance + self.OVERDRAFT_LIMIT:
            raise ValueError("Withdrawal exceeds overdraft limit.")
        self._set_balance_allow_overdraft(self.balance - amount)
        self._log_transaction(f"Withdrew ₹{amount} (overdraft used if applicable)")
        return self.balance

    def calculate_interest(self):
        # Current accounts typically earn no interest.
        return 0.0


class FixedDepositAccount(Account):

    INTEREST_RATE = 0.07          # 7% annual interest, higher than savings

    def __init__(self, account_holder, balance, tenure_years):
        super().__init__(account_holder, balance)
        self.tenure_years = tenure_years

    def withdraw(self, amount):
        # Polymorphism: fixed deposits don't allow withdrawal at all.
        raise PermissionError("Premature withdrawal not allowed on a Fixed Deposit account.")

    def calculate_interest(self):
        # Compound interest over the tenure.
        maturity_value = self.balance * ((1 + self.INTEREST_RATE) ** self.tenure_years)
        interest = maturity_value - self.balance
        return round(interest, 2)


# -------------------------------------------------------------------
# 5. COMPOSITION (a "has-a" relationship, complementing inheritance)
# A Bank doesn't inherit from Account — it just manages a collection
# of Account objects.
# -------------------------------------------------------------------
class Bank:

    def __init__(self, name):
        self.name = name
        self.accounts = []

    def open_account(self, account):
        self.accounts.append(account)
        print(f"✔ Account opened: {account}")
        return account

    def total_deposits(self):
        return sum(acc.balance for acc in self.accounts)

    def find_account(self, account_number):
        for acc in self.accounts:
            if acc.account_number == account_number:
                return acc
        return None

    def transfer(self, from_acc, to_acc, amount):
        from_acc.withdraw(amount)
        to_acc.deposit(amount)
        print(f"✔ Transferred ₹{amount} from {from_acc.account_number} to {to_acc.account_number}")


# -------------------------------------------------------------------
# DEMO — run the program to see every concept in action
# -------------------------------------------------------------------
def main():
    print("=" * 70)
    print("BANKING SYSTEM — OOP CONCEPTS DEMO")
    print("=" * 70)

    bank = Bank("Lilly National Bank")

    # --- Creating objects (instantiation) ---
    savings = SavingsAccount("Dhanasai", 5000)
    current = CurrentAccount("Phani", 2000)
    fd = FixedDepositAccount("Joseph", 100000, tenure_years=3)

    bank.open_account(savings)
    bank.open_account(current)
    bank.open_account(fd)

    print("\n--- Encapsulation: balance accessed only via property ---")
    print(f"Savings balance (via getter): ₹{savings.balance}")
    try:
        savings.balance = -500          # setter validates and rejects this
    except ValueError as e:
        print(f"Blocked invalid update: {e}")

    print("\n--- Polymorphism: same method name, different behaviour ---")
    for acc in (savings, current, fd):
        print(f"{acc.__class__.__name__}.calculate_interest() -> ₹{acc.calculate_interest()}")

    print("\n--- Polymorphism: withdraw() behaves differently per account type ---")
    try:
        savings.withdraw(4900)          # breaches minimum balance rule
    except ValueError as e:
        print(f"SavingsAccount blocked: {e}")

    try:
        current.withdraw(10500)         # uses overdraft, within limit
        print(f"CurrentAccount after overdraft withdrawal: ₹{current.balance}")
    except ValueError as e:
        print(f"CurrentAccount blocked: {e}")

    try:
        fd.withdraw(1000)               # not allowed at all
    except PermissionError as e:
        print(f"FixedDepositAccount blocked: {e}")

    print("\n--- Bank transfer (composition in action) ---")
    bank.transfer(current, savings, 500)

    print("\n--- Dunder methods ---")
    print(f"str(savings)  -> {savings}")
    print(f"repr(savings) -> {repr(savings)}")
    print(f"savings == current -> {savings == current}")
    print(f"savings + current (combined balance) -> ₹{savings + current}")

    print("\n--- Class method & static method ---")
    print(f"Total accounts opened so far: {Account.get_total_accounts()}")
    print(f"Is 500 a valid amount? {Account.is_valid_amount(500)}")
    print(f"Is -50 a valid amount? {Account.is_valid_amount(-50)}")

    print("\n--- Bank-level aggregation ---")
    print(f"Total deposits in {bank.name}: ₹{bank.total_deposits():.2f}")

    print("\n--- Transaction history for Savings account ---")
    for entry in savings.transaction_history:
        print(" ", entry)

    print("\n--- Trying to instantiate the abstract base class directly ---")
    try:
        Account("Someone", 100)
    except TypeError as e:
        print(f"Blocked as expected: {e}")


if __name__ == "__main__":
    main()