class PlayerProfile():
    def __init__(self, money=2500):
        self.money = money

    def add_money(self, money):
        self.money += money